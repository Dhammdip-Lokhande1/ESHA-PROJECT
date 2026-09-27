import asyncio
import csv
import json
import sys
import uuid
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.session import create_tables, get_db
from app.db.models import Feedback, FusionWeightHistory, Run, Evidence
from app.fusion.adaptive_trainer import retrain_fusion_weights
from app.fusion.fusion_engine import fuse
from app.preprocessing.preprocess import parse_ast, tokenize_code
from app.similarity.lexical import lexical_similarity
from app.similarity.structural import structural_similarity
from app.similarity.semantic import semantic_similarity
from app.similarity.behavioral import behavioral_similarity
from app.explain.ai_generation_detector import detect_ai_generated
from app.explain.transformation_detector import detect_transformation
from app.explain.explanation_generator import generate_explanation
from sqlalchemy import select, delete

def load_dataset(dataset_dir):
    metadata_csv = dataset_dir / "metadata.csv"
    pairs_dir = dataset_dir / "pairs"
    pairs = []
    with open(metadata_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["pair_id"]
            label = int(row["label"])
            pairs.append({
                "pair_id": pid,
                "file_a_path": pairs_dir / pid / "code_a.py",
                "file_b_path": pairs_dir / pid / "code_b.py",
                "file_a_name": f"{pid}_code_a.py",
                "file_b_name": f"{pid}_code_b.py",
                "label": label,
            })
    return pairs

async def main():
    print("--- Part 1: Real Pipeline DB Population & Adaptive Weight Training ---")
    await create_tables()

    root_dir = Path(__file__).parent
    ds_dir = root_dir / "dataset"
    
    all_pairs = load_dataset(ds_dir)
    print(f"Processing {len(all_pairs)} benchmark pairs using REAL pipeline...")

    async with get_db() as db:
        # Clear old runs & feedback to have a clean, accurate DB state
        await db.execute(delete(Feedback))
        await db.execute(delete(Evidence))
        await db.execute(delete(Run))
        await db.flush()

        for idx, p in enumerate(all_pairs, 1):
            code_a = p["file_a_path"].read_text(encoding="utf-8", errors="replace")
            code_b = p["file_b_path"].read_text(encoding="utf-8", errors="replace")

            tokens_a = tokenize_code(code_a)
            tokens_b = tokenize_code(code_b)
            ast_a = parse_ast(code_a)
            ast_b = parse_ast(code_b)

            lex, _ = lexical_similarity(tokens_a, tokens_b)
            struct, _ = structural_similarity(ast_a, ast_b)
            sem, _ = semantic_similarity(code_a, code_b)
            beh, _ = behavioral_similarity(code_a, code_b, [])

            scores = {"lexical": lex, "structural": struct, "semantic": sem, "behavioral": beh}
            fusion_score, weight_metadata = fuse(scores)

            ai_a, _ = detect_ai_generated(code_a)
            ai_b, _ = detect_ai_generated(code_b)
            ai_likelihood = max(ai_a, ai_b)

            scores_with_fusion = {**scores, "fusion": fusion_score}
            transformation = detect_transformation(scores_with_fusion, ai_likelihood)
            explanation = generate_explanation(scores_with_fusion, transformation, [])

            run_id = str(uuid.uuid4())
            run = Run(
                id=run_id,
                file_a_name=p["file_a_name"],
                file_b_name=p["file_b_name"],
                lexical_score=lex,
                structural_score=struct,
                semantic_score=sem,
                behavioral_score=beh,
                fusion_score=fusion_score,
                fusion_weights_used=json.dumps(weight_metadata.get("effective_weights", {})),
                transformation_type=transformation.get("type"),
                transformation_confidence=transformation.get("confidence"),
                ai_generation_likelihood=ai_likelihood,
                explanation=json.dumps(explanation),
            )
            db.add(run)

            verdict = "confirmed" if p["label"] == 1 else "false_positive"
            fb = Feedback(run_id=run_id, verdict=verdict)
            db.add(fb)

            if idx % 10 == 0 or idx == len(all_pairs):
                print(f"  Processed {idx}/{len(all_pairs)} pairs...")

        await db.flush()

        # Call retrain_fusion_weights
        res = await retrain_fusion_weights(db)
        print("\nRetraining Result:")
        print(json.dumps(res, indent=2))

        # Verify DB entry in FusionWeightHistory
        stmt = select(FusionWeightHistory).order_by(FusionWeightHistory.created_at.desc()).limit(1)
        latest = (await db.execute(stmt)).scalar_one_or_none()
        assert latest is not None, "FusionWeightHistory entry missing!"
        print(f"\nPersisted in DB table 'fusion_weight_history' at {latest.created_at}:")
        print(f"Weights: {latest.weights}")
        print(f"Trained on: {latest.trained_on_n_samples} samples")

if __name__ == "__main__":
    asyncio.run(main())
