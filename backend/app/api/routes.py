"""
api/routes.py — Thin orchestration layer.

M2 status:
  - POST /analyze  — full pipeline: preprocessing → lexical → structural →
                     semantic → fusion + evidence persisted to DB
  - All other endpoints stubbed until their respective milestones.

No business logic lives here — all computation is delegated to the
similarity/fusion modules. This file is orchestration only.

AGENTS.md non-negotiable reminder:
  - Evidence MUST be persisted to the evidence table (not just returned in JSON).
  - Behavioral module MUST be wired in M4 — it is stubbed as None here but
    explicitly noted with a TODO that must be verified in M4's review pass.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Annotated, Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_current_user,
    get_current_user_optional,
    require_role,
    verify_run_access,
)
from app.auth.rate_limiter import rate_limit
from app.config import settings
from app.db.models import Evidence, Feedback, FusionWeightHistory, Run, User
from app.db.session import get_db_dependency
from app.explain.ai_generation_detector import detect_ai_generated
from app.explain.confidence import compute_confidence_indicators
from app.explain.explanation_generator import generate_explanation
from app.explain.transformation_detector import detect_transformation
from app.fusion.adaptive_trainer import retrain_fusion_weights
from app.fusion.fusion_engine import async_load_current_weights, fuse
from app.preprocessing.preprocess import parse_ast, tokenize_code
from app.similarity.behavioral import behavioral_similarity
from app.similarity.lexical import lexical_similarity
from app.similarity.semantic import semantic_similarity
from app.similarity.structural import structural_similarity

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic request / response models
# ──────────────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    submission_code: str = Field(..., description="Python source code of submission A")
    reference_code: str = Field(..., description="Python source code of submission B / reference")
    file_a_name: Optional[str] = Field(None, description="Filename for submission A (optional)")
    file_b_name: Optional[str] = Field(None, description="Filename for submission B (optional)")
    test_inputs: list[str] = Field(
        default_factory=list,
        description="Optional test inputs for behavioral module (wired in M4)",
    )

    @field_validator("submission_code", "reference_code")
    @classmethod
    def validate_size(cls, v: str) -> str:
        if len(v.encode("utf-8")) > settings.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"Code exceeds the {settings.MAX_FILE_SIZE_BYTES // 1024} KB size limit."
            )
        return v

    @field_validator("test_inputs")
    @classmethod
    def validate_test_inputs(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Maximum of 10 test_inputs allowed per request.")
        for item in v:
            if len(item) > 256:
                raise ValueError("Each test_input item must not exceed 256 characters.")
        return v


class ComponentScores(BaseModel):
    lexical: Optional[float]
    structural: Optional[float]
    semantic: Optional[float]
    behavioral: Optional[float]  # None until M4

    lexical_evidence: list[dict]
    structural_evidence: list[dict]
    semantic_evidence: list[dict]
    behavioral_evidence: list[dict]


class AnalyzeResponse(BaseModel):
    run_id: str
    fusion_score: Optional[float]
    fusion_weight_metadata: Optional[dict]  # Required by Non-Negotiable Rule 5

    components: ComponentScores

    # M3: Populated now
    explanation: Optional[dict]   # full explanation dict from generate_explanation()
    ai_generation: Optional[dict] # M3.5
    confidence_indicators: Optional[dict]  # M5


class FeedbackRequest(BaseModel):
    verdict: Literal["confirmed", "false_positive"]


# ──────────────────────────────────────────────────────────────────────────────
# Helper: persist evidence items to DB
# ──────────────────────────────────────────────────────────────────────────────

async def _persist_evidence(
    db: AsyncSession,
    run_id: str,
    dimension: str,
    evidence_items: list[dict],
    file_ref: Optional[str] = None,
) -> None:
    """
    Persist a list of evidence items to the evidence table.

    CRITICAL: evidence MUST be written to the DB, not just returned in API JSON.
    This was silently skipped in a prior build. Each item in evidence_items
    becomes one row with detail = JSON(item).
    """
    for item in evidence_items:
        ev = Evidence(
            run_id=run_id,
            dimension=dimension,
            file_ref=file_ref,
            line_start=item.get("line_start"),
            line_end=item.get("line_end"),
            detail=json.dumps(item),
        )
        db.add(ev)


# ──────────────────────────────────────────────────────────────────────────────
# POST /analyze
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze two Python code submissions",
    description=(
        "Full pipeline: lexical + structural (M1) + semantic (M2) + fusion (M2). "
        "Behavioral (M4) stubbed as None. Every score is paired with evidence "
        "items that are persisted to the DB. "
        "Non-Negotiable Rule 2: no bare float reaches the response without evidence."
    ),
    dependencies=[Depends(rate_limit(max_requests=30, window_seconds=60, key_prefix="analyze"))],
)
async def analyze(
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AnalyzeResponse:
    run_id = str(uuid.uuid4())

    # ── Preprocessing & Concurrent Pipelines ───────────────────────────────
    tokens_a = tokenize_code(body.submission_code)
    tokens_b = tokenize_code(body.reference_code)
    ast_a = parse_ast(body.submission_code)
    ast_b = parse_ast(body.reference_code)

    # Run independent similarity modules and AI detection in parallel threads
    (
        (lex_score, lex_evidence),
        (struct_score, struct_evidence),
        (sem_score, sem_evidence),
        (beh_score, beh_evidence),
        (ai_a, evidence_a),
        (ai_b, evidence_b),
    ) = await asyncio.gather(
        asyncio.to_thread(lexical_similarity, tokens_a, tokens_b),
        asyncio.to_thread(structural_similarity, ast_a, ast_b),
        asyncio.to_thread(semantic_similarity, body.submission_code, body.reference_code),
        asyncio.to_thread(behavioral_similarity, body.submission_code, body.reference_code, body.test_inputs),
        asyncio.to_thread(detect_ai_generated, body.submission_code),
        asyncio.to_thread(detect_ai_generated, body.reference_code),
    )

    # ── Fusion (M2 & M4.5) ──────────────────────────────────────────────────
    scores = {
        "lexical": lex_score,
        "structural": struct_score,
        "semantic": sem_score,
        "behavioral": beh_score,  # None if stub — excluded from fusion gracefully
    }
    
    current_weights, weight_source, last_updated = await async_load_current_weights(db)
    fusion_score, weight_metadata = fuse(
        scores, weights=current_weights, source=weight_source, last_updated=last_updated
    )

    # ── Transformation detection + Explanation (M3 & M3.5) ─────────────────
    scores_with_fusion = {
        **scores,
        "fusion": fusion_score,
    }
    
    if ai_a >= ai_b:
        ai_likelihood = ai_a
        ai_evidence = evidence_a
    else:
        ai_likelihood = ai_b
        ai_evidence = evidence_b

    transformation = detect_transformation(scores_with_fusion, ai_likelihood)
    explanation = generate_explanation(scores_with_fusion, transformation, ai_evidence)

    # ── Persist Run to DB ──────────────────────────────────────────────────
    user_id_val = current_user.id if (current_user and isinstance(current_user, User)) else None
    run = Run(
        id=run_id,
        user_id=user_id_val,
        file_a_name=body.file_a_name or "Submission.py",
        file_b_name=body.file_b_name or "Reference.py",
        lexical_score=lex_score,
        structural_score=struct_score,
        semantic_score=sem_score,
        behavioral_score=beh_score,
        fusion_score=fusion_score,
        fusion_weights_used=json.dumps(weight_metadata.get("effective_weights", {})),
        transformation_type=transformation.get("type"),
        transformation_confidence=transformation.get("confidence"),
        ai_generation_likelihood=ai_likelihood,
        explanation=json.dumps(explanation),
    )
    db.add(run)

    # ── Confidence Indicators (M5) ─────────────────────────────────────────
    confidence_indicators = compute_confidence_indicators(
        tokens_a, tokens_b, ast_a, ast_b, sem_score, sem_evidence, beh_score, beh_evidence
    )

    # ── Persist Evidence to DB ─────────────────────────────────────────────
    # CRITICAL (AGENTS.md): evidence MUST be persisted to DB, not just returned
    # in API JSON. Includes lexical, structural, semantic, behavioral, and ai_generation.
    await _persist_evidence(db, run_id, "lexical", lex_evidence)
    await _persist_evidence(db, run_id, "structural", struct_evidence)
    await _persist_evidence(db, run_id, "semantic", sem_evidence)
    await _persist_evidence(db, run_id, "behavioral", beh_evidence)
    await _persist_evidence(db, run_id, "ai_generation", ai_evidence)

    # Session commits automatically when the Depends context exits
    await db.flush()  # Ensure run + evidence are written before response

    # ── Build response ─────────────────────────────────────────────────────
    return AnalyzeResponse(
        run_id=run_id,
        fusion_score=fusion_score,
        fusion_weight_metadata=weight_metadata,
        components=ComponentScores(
            lexical=lex_score,
            structural=struct_score,
            semantic=sem_score,
            behavioral=beh_score,
            lexical_evidence=lex_evidence,
            structural_evidence=struct_evidence,
            semantic_evidence=sem_evidence,
            behavioral_evidence=beh_evidence,
        ),
        explanation=explanation,
        ai_generation={
            "likelihood": ai_likelihood,
            "evidence": ai_evidence,
        },
        confidence_indicators=confidence_indicators,
    )



# ──────────────────────────────────────────────────────────────────────────────
# POST /feedback/{run_id}
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# POST /feedback/{run_id}
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# POST /feedback/{run_id}
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/feedback/{run_id}",
    status_code=status.HTTP_200_OK,
    summary="Submit analysis verdict for a run",
)
async def submit_feedback(
    run_id: str,
    body: FeedbackRequest,
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(require_role("user", "admin")),
    run: Run = Depends(verify_run_access),
) -> dict:
    """
    Persist user verdict. Requires user or admin role and ownership/access rights (IDOR protected).
    """

    fb = Feedback(
        run_id=run_id,
        user_id=current_user.id,
        verdict=body.verdict,
    )
    db.add(fb)

    return {"status": "ok", "run_id": run_id, "verdict": body.verdict}


# ──────────────────────────────────────────────────────────────────────────────
# GET /runs
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/runs", summary="List past analysis runs")
async def list_runs(
    limit: int = 50,
    sort: str = "created_at",
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Returns recent runs for authenticated user.
    Normal users see only their own runs.
    Admins see all runs.
    """
    from sqlalchemy import select  # noqa: PLC0415

    if current_user.role == "user":
        stmt = (
            select(Run)
            .where(Run.user_id == current_user.id)
            .order_by(Run.created_at.desc())
            .limit(min(limit, 200))
        )
    else:
        stmt = select(Run).order_by(Run.created_at.desc()).limit(min(limit, 200))

    result = await db.execute(stmt)
    runs = result.scalars().all()

    return {
        "runs": [
            {
                "id": r.id,
                "file_a_name": r.file_a_name or "Submission.py",
                "file_b_name": r.file_b_name or "Reference.py",
                "fusion_score": r.fusion_score,
                "lexical_score": r.lexical_score,
                "structural_score": r.structural_score,
                "semantic_score": r.semantic_score,
                "behavioral_score": r.behavioral_score,
                "transformation_type": r.transformation_type,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ]
    }


# ──────────────────────────────────────────────────────────────────────────────
# POST /runs/{run_id}/claim
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/runs/{run_id}/claim",
    status_code=status.HTTP_200_OK,
    summary="Claim an unassigned guest run to save it to user history",
)
async def claim_run(
    run_id: str,
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Associates an unassigned guest run with the currently authenticated user."""
    from sqlalchemy import select  # noqa: PLC0415
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    if run.user_id is not None and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. This run belongs to another user and cannot be claimed.",
        )

    run.user_id = current_user.id
    await db.commit()

    return {
        "status": "ok",
        "message": f"Run '{run_id}' successfully saved to your account.",
        "run_id": run.id,
        "claimed_by": current_user.id,
    }


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /runs/{run_id}
# ──────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/runs/{run_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a specific investigation run",
)
async def delete_run(
    run_id: str,
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(get_current_user),
    run: Run = Depends(verify_run_access),
) -> dict:
    """Deletes an investigation run after verifying ownership/permissions (IDOR protected)."""
    from sqlalchemy import delete  # noqa: PLC0415

    if current_user.role == "user" and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. You can only delete your own analysis runs.",
        )

    await db.execute(delete(Run).where(Run.id == run.id))
    await db.commit()

    return {"status": "ok", "message": f"Run '{run.id}' successfully deleted."}


# ──────────────────────────────────────────────────────────────────────────────
# GET /fusion/weights
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/fusion/weights", summary="Get current fusion weights")
async def get_fusion_weights(
    db: AsyncSession = Depends(get_db_dependency),
) -> dict:
    """Returns current weights and full retraining history (M4.5 adds adaptive)."""
    from sqlalchemy import select  # noqa: PLC0415

    current_weights, source, last_updated = await async_load_current_weights(db)

    stmt = select(FusionWeightHistory).order_by(
        FusionWeightHistory.created_at.desc()
    ).limit(10)
    result = await db.execute(stmt)
    history = result.scalars().all()

    return {
        "current_weights": current_weights,
        "source": source,
        "last_updated": last_updated,
        "history": [
            {
                "weights": json.loads(h.weights),
                "trained_on_n_samples": h.trained_on_n_samples,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ],
    }


# ──────────────────────────────────────────────────────────────────────────────
# POST /fusion/retrain  (M4.5)
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/fusion/retrain",
    summary="Trigger adaptive fusion retraining",
    dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, key_prefix="retrain"))],
)
async def retrain_fusion(
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Adaptive retraining from feedback (Requires admin role only as it modifies system-wide fusion weights)."""
    result = await retrain_fusion_weights(db)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ──────────────────────────────────────────────────────────────────────────────
# GET /dashboard/summary  (M6)
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# Dashboard & Analytics Endpoints (Four-Context Scoped)
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/dashboard/my",
    summary="Authenticated Student Personal Dashboard Metrics",
    description="Returns metrics and history strictly scoped to the authenticated user (user_id == current_user.id).",
)
async def my_dashboard_summary(
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Personal analysis metrics for currently authenticated user."""
    from sqlalchemy import func, select  # noqa: PLC0415
    from app.db.models import Run  # noqa: PLC0415

    # Filter strictly by user_id
    total_stmt = select(func.count()).select_from(Run).where(Run.user_id == current_user.id)
    total = await db.scalar(total_stmt) or 0

    avg_stmt = select(func.avg(Run.fusion_score)).where(Run.user_id == current_user.id)
    avg_fusion = await db.scalar(avg_stmt)

    flagged_stmt = (
        select(func.count())
        .select_from(Run)
        .where(Run.user_id == current_user.id, Run.fusion_score >= 0.8)
    )
    flagged = await db.scalar(flagged_stmt) or 0

    # 1. User Transformation Breakdown
    trans_stmt = (
        select(Run.transformation_type, func.count())
        .where(Run.user_id == current_user.id)
        .group_by(Run.transformation_type)
    )
    trans_result = await db.execute(trans_stmt)
    transformation_breakdown = [
        {"name": row[0] or "Unknown", "value": row[1]}
        for row in trans_result.all()
    ]

    # 2. User Score Distribution
    scores_stmt = select(Run.fusion_score).where(
        Run.user_id == current_user.id, Run.fusion_score != None
    )
    scores_result = await db.execute(scores_stmt)
    scores = [s for s in scores_result.scalars().all() if s is not None]

    bins = [0] * 10
    for s in scores:
        idx = min(int(s * 10), 9)
        bins[idx] += 1

    score_distribution = [
        {"bucket": f"{i/10:.1f}-{(i+1)/10:.1f}", "count": count}
        for i, count in enumerate(bins)
    ]

    # 3. Recent runs
    recent_stmt = (
        select(Run)
        .where(Run.user_id == current_user.id)
        .order_by(Run.created_at.desc())
        .limit(5)
    )
    recent_result = await db.execute(recent_stmt)
    recent_runs = [
        {
            "id": r.id,
            "file_a_name": r.file_a_name or "Submission.py",
            "file_b_name": r.file_b_name or "Reference.py",
            "fusion_score": r.fusion_score,
            "transformation_type": r.transformation_type,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_result.scalars().all()
    ]

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_runs": total,
        "flagged_count": flagged,
        "avg_fusion_score": round(float(avg_fusion), 4) if avg_fusion else 0.0,
        "score_distribution": score_distribution,
        "transformation_breakdown": transformation_breakdown,
        "recent_runs": recent_runs,
    }


@router.get(
    "/instructor/dashboard",
    summary="User & Admin Analytics & Calibration Dashboard",
    description="Returns aggregate statistics across registered submission runs, feedback calibration matrix, and fusion weight drift.",
)
@router.get(
    "/analytics/summary",
    summary="User & Admin Analytics & Calibration Dashboard",
    description="Returns aggregate statistics across registered submission runs, feedback calibration matrix, and fusion weight drift.",
)
async def instructor_dashboard_summary(
    db: AsyncSession = Depends(get_db_dependency),
    current_user: User = Depends(require_role("user", "admin")),
) -> dict:
    """Class aggregate metrics, feedback calibration, and retraining audit log."""
    from sqlalchemy import func, select  # noqa: PLC0415
    from app.db.models import Run, Feedback, FusionWeightHistory  # noqa: PLC0415

    # Filter for student/registered runs (excluding benchmark and guest runs if desired)
    student_runs_where = Run.user_id.is_not(None)

    total = await db.scalar(select(func.count()).select_from(Run).where(student_runs_where)) or 0
    avg_fusion = await db.scalar(select(func.avg(Run.fusion_score)).where(student_runs_where))
    flagged = await db.scalar(
        select(func.count())
        .select_from(Run)
        .where(student_runs_where, Run.fusion_score >= 0.8)
    ) or 0

    # 1. Transformation Breakdown across student runs
    trans_stmt = (
        select(Run.transformation_type, func.count())
        .where(student_runs_where)
        .group_by(Run.transformation_type)
    )
    trans_result = await db.execute(trans_stmt)
    transformation_breakdown = [
        {"name": row[0] or "Unknown", "value": row[1]}
        for row in trans_result.all()
    ]

    # 2. Score Distribution
    scores_stmt = select(Run.fusion_score).where(student_runs_where, Run.fusion_score != None)
    scores_result = await db.execute(scores_stmt)
    scores = [s for s in scores_result.scalars().all() if s is not None]

    bins = [0] * 10
    for s in scores:
        idx = min(int(s * 10), 9)
        bins[idx] += 1

    score_distribution = [
        {"bucket": f"{i/10:.1f}-{(i+1)/10:.1f}", "count": count}
        for i, count in enumerate(bins)
    ]

    # 3. Weight Drift History
    drift_stmt = select(FusionWeightHistory).order_by(FusionWeightHistory.created_at.asc())
    drift_result = await db.execute(drift_stmt)
    weight_drift_history = []
    for h in drift_result.scalars().all():
        w = json.loads(h.weights)
        weight_drift_history.append({
            "date": h.created_at.isoformat() if h.created_at else "",
            "lexical": w.get("lexical", 0.25),
            "structural": w.get("structural", 0.25),
            "semantic": w.get("semantic", 0.25),
            "behavioral": w.get("behavioral", 0.25),
            "samples": h.trained_on_n_samples
        })

    # 4. Calibration Data (Feedback records)
    calib_stmt = select(Run.fusion_score, Feedback.verdict).join(
        Feedback, Run.id == Feedback.run_id
    )
    calib_result = await db.execute(calib_stmt)
    calibration_data = [
        {"score": row[0], "verdict": row[1]}
        for row in calib_result.all()
        if row[0] is not None
    ]

    return {
        "total_runs": total,
        "flagged_count": flagged,
        "avg_fusion_score": round(float(avg_fusion), 4) if avg_fusion else 0.0,
        "score_distribution": score_distribution,
        "transformation_breakdown": transformation_breakdown,
        "weight_drift_history": weight_drift_history,
        "calibration_data": calibration_data,
    }


@router.get(
    "/research/evaluation",
    summary="Research Benchmark Offline Evaluation Data",
    description="Returns metrics from the 180-pair benchmark dataset (30 program families, 6 categories). Completely decoupled from live user analysis.",
)
async def research_evaluation_summary() -> dict:
    """Static research evaluation dataset summary (EHSA 150-pair benchmark + IBM CodeNet 100-pair controlled subset)."""
    return {
        "dataset_name": "EHSA Research Benchmark v1.0 & IBM CodeNet Controlled Subset",
        "total_pairs": 250,
        "benchmark_pairs": 150,
        "codenet_pairs": 100,
        "program_families": 30,
        "categories": [
            {"name": "exact_copy", "count": 30, "description": "Identical code / whitespace and comment variations"},
            {"name": "variable_renaming", "count": 30, "description": "Identifier & parameter renaming"},
            {"name": "structural_refactoring", "count": 30, "description": "Control flow & loop restructuring"},
            {"name": "ai_rewrite", "count": 30, "description": "LLM-generated code rewrites"},
            {"name": "unrelated", "count": 30, "description": "Different algorithms & logic"},
        ],
        "evaluation_methodology": "5-Fold Grouped Cross-Validation (Grouped by Source Program ID)",
        "results": {
            "adaptive_fusion_f1": 0.916,
            "equal_weights_f1": 0.868,
            "lexical_only_f1": 0.400,
            "structural_only_f1": 0.598,
            "semantic_only_f1": 0.882,
            "auc_roc": 0.887,
            "ehsa_benchmark_f1": 0.997,
            "ehsa_benchmark_auc": 1.000,
            "codenet_research_fusion_f1": 0.896,
            "codenet_research_fusion_auc": 0.941,
            "codenet_semantic_only_f1": 0.882,
            "codenet_fixed_fusion_f1": 0.868,
        },
    }



@router.get("/dashboard/summary", summary="Legacy Dashboard summary router")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> dict:
    """Routes callers to appropriate context summary based on identity."""
    if current_user and current_user.role in ("user", "admin"):
        return await instructor_dashboard_summary(db, current_user)
    elif current_user:
        return await my_dashboard_summary(db, current_user)
    else:
        # Guests receive guest mode notice - no aggregate data leaking
        return {
            "guest_mode": True,
            "message": "Guest session. Perform an analysis to view your session results.",
            "total_runs": 0,
            "flagged_count": 0,
            "avg_fusion_score": 0.0,
            "score_distribution": [],
            "transformation_breakdown": [],
            "weight_drift_history": [],
            "calibration_data": [],
        }


# ──────────────────────────────────────────────────────────────────────────────
# POST /compare/batch (M7)
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/compare/batch",
    status_code=status.HTTP_200_OK,
    summary="Batch pairwise comparison for multiple files (M7)",
    dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60, key_prefix="batch"))],
)
async def compare_batch(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> dict:
    """Accepts a list of files and performs O(n²) comparisons."""
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed for batch processing.")
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required for comparison.")

    # Read all files into memory (safe since limit is 20 and size limit is enforced elsewhere)
    file_contents = {}
    for f in files:
        if not f.filename:
            continue
        # Only read files up to reasonable size (e.g. 1MB)
        content = await f.read()
        if len(content) > 1_000_000:
            raise HTTPException(status_code=422, detail=f"File {f.filename} exceeds 1MB limit.")
        file_contents[f.filename] = content.decode("utf-8")

    filenames = list(file_contents.keys())
    matrix = []

    # O(n²) comparisons
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            f_a = filenames[i]
            f_b = filenames[j]
            
            req = AnalyzeRequest(
                submission_code=file_contents[f_a],
                reference_code=file_contents[f_b],
                file_a_name=f_a,
                file_b_name=f_b,
                test_inputs=[]
            )
            
            # Reuse the existing analyze logic internally with authenticated user context
            resp = await analyze(req, db, current_user)
            
            matrix.append({
                "run_id": resp.run_id,
                "file_a": f_a,
                "file_b": f_b,
                "fusion_score": resp.fusion_score,
                "transformation_type": resp.explanation.get("transformation_type") if resp.explanation else "Unknown"
            })

    return {"matrix": matrix}


# ──────────────────────────────────────────────────────────────────────────────
# GET /report/{run_id} (M8)
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/report/{run_id}",
    summary="Export run evidence (M8)",
)
async def get_report(
    run_id: str,
    format: Literal["json", "html", "pdf"] = "json",
    db: AsyncSession = Depends(get_db_dependency),
    run: Run = Depends(verify_run_access),
) -> Any:
    """Exports a specific run and its evidence in JSON, HTML, or PDF format (IDOR Protected)."""
    from sqlalchemy import select
    from app.db.models import Evidence

    # Fetch evidence
    ev_stmt = select(Evidence).where(Evidence.run_id == run.id)
    ev_result = await db.execute(ev_stmt)
    evidence_items = ev_result.scalars().all()

    # Build dict
    data = {
        "run_id": run.id,
        "file_a_name": run.file_a_name,
        "file_b_name": run.file_b_name,
        "scores": {
            "fusion": run.fusion_score,
            "lexical": run.lexical_score,
            "structural": run.structural_score,
            "semantic": run.semantic_score,
            "behavioral": run.behavioral_score,
        },
        "transformation": run.transformation_type,
        "ai_generation": run.ai_generation_likelihood,
        "explanation": json.loads(run.explanation) if run.explanation else None,
        "evidence": [
            {
                "dimension": e.dimension,
                "file_ref": e.file_ref,
                "line_start": e.line_start,
                "line_end": e.line_end,
                "detail": json.loads(e.detail)
            }
            for e in evidence_items
        ],
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }

    if format == "json":
        # Force a file download
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="ehsa_report_{run_id[:8]}.json"'}
        )
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EHSA Report - {run_id[:8]}</title>
        <style>
            body {{ font-family: sans-serif; padding: 2rem; color: #333; }}
            h1 {{ color: #2563eb; }}
            .summary {{ background: #f8fafc; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; border: 1px solid #e2e8f0; }}
            .score {{ font-size: 1.5rem; font-weight: bold; color: #dc2626; }}
            .evidence-section {{ margin-bottom: 2rem; }}
            .evidence-item {{ background: #fff; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.25rem; margin-bottom: 1rem; }}
            pre {{ background: #f1f5f9; padding: 0.5rem; border-radius: 0.25rem; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>EHSA Investigation Report</h1>
        <p><strong>Run ID:</strong> {run_id}</p>
        <p><strong>Date:</strong> {data["created_at"]}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>File A:</strong> {data["file_a_name"] or "Unknown"}</p>
            <p><strong>File B:</strong> {data["file_b_name"] or "Unknown"}</p>
            <p><strong>Fusion Score:</strong> <span class="score">{(data["scores"]["fusion"] or 0) * 100:.1f}%</span></p>
            <p><strong>Transformation Profile:</strong> {data["transformation"] or "N/A"}</p>
        </div>
        
        <h2>Evidence Log</h2>
        <div class="evidence-section">
            <h3>Lexical ({data["scores"]["lexical"]})</h3>
            <ul>{"".join(f'<li>{e["detail"].get("note", str(e["detail"]))}</li>' for e in data["evidence"] if e["dimension"] == "lexical")}</ul>
        </div>
        <div class="evidence-section">
            <h3>Structural ({data["scores"]["structural"]})</h3>
            <ul>{"".join(f'<li>{e["detail"].get("note", str(e["detail"]))}</li>' for e in data["evidence"] if e["dimension"] == "structural")}</ul>
        </div>
        <div class="evidence-section">
            <h3>Semantic ({data["scores"]["semantic"]})</h3>
            <ul>{"".join(f'<li>{e["detail"].get("note", str(e["detail"]))}</li>' for e in data["evidence"] if e["dimension"] == "semantic")}</ul>
        </div>
    </body>
    </html>
    """

    if format == "pdf":
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="ehsa_report_{run_id[:8]}.pdf"'}
            )
        except Exception as exc:
            # Fall back to HTML download if WeasyPrint or native GTK bindings are unavailable
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": f'attachment; filename="ehsa_report_{run_id[:8]}.html"'}
            )

    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="ehsa_report_{run_id[:8]}.html"'}
    )


