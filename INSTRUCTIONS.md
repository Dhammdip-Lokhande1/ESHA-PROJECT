# INSTRUCTIONS.md
## EHSA — Explainable Hybrid Similarity Analyzer
### Master build guide — read this file completely before writing any code

This is the single source of truth for building this project from scratch. It supersedes any prior partial docs. An AI coding agent (Antigravity, Claude Code, Cursor) should read this file fully, confirm understanding of the current milestone, and only then begin work — see section 14 (Build Order) for the sequencing.

---

## 1. Project Identity

**Name:** EHSA — Explainable Hybrid Similarity Analyzer
**Formal title (for the paper):** An Explainable Hybrid Framework for Source Code Similarity Analysis Using Lexical, Structural, and Semantic Representations, with Adaptive Evidence Fusion

**What it is not:** Not a plagiarism accusation engine. Not the first tool to use lexical/AST/semantic methods (these exist independently and in combination — see section 15, References). Not a black-box AI-code detector.

**What it actually is:** A source-code similarity *investigation* tool that answers "why are these programs similar?" instead of just "how similar are they?" — every score is required to carry traceable evidence, the fusion of signals adapts based on real instructor feedback rather than staying at fixed hand-picked weights, and both a static robustness signal (behavioral execution) and an AI-authorship signal are integrated into the same evidence-first pipeline rather than bolted on separately.

---

## 2. Core Objectives

| ID | Objective |
|---|---|
| G1 | Detect similarity across 4 dimensions: lexical, structural, semantic, behavioral |
| G2 | Every score carries traceable evidence — no bare numbers reach the user, ever |
| G3 | Classify the transformation type (renaming, refactoring, AI-rewrite, exact copy, unrelated) |
| G4 | Detect AI-generated code as its own evidence-backed signal, not a footnote |
| G5 | **Fusion weights adapt from real instructor feedback** — not fixed at design time |
| G6 | Zero cost — no paid APIs, no paid hosting tier required to run the full system |
| G7 | Usable by a non-technical instructor via a genuinely good dashboard (see section 9) |
| G8 | Produce reproducible, citable results suitable for a research paper |

---

## 3. Research Questions (what the evaluation must answer)

| ID | Question | Answered by |
|---|---|---|
| RQ1 | Can lexical, structural, semantic, and behavioral signals be effectively combined? | Fusion engine + integration tests |
| RQ2 | Does fusion outperform any individual signal, and does *learned/adaptive* fusion outperform *fixed-weight* fusion? | Ablation study: fixed vs. learned fusion, each dimension standalone vs. combined |
| RQ3 | Does evidence-grounded explanation improve instructor understanding and trust? | Instructor user study (task-based + survey) |
| RQ4 | How robust is the framework against AI-assisted code transformation? | Dedicated AI-generation-detection module, tested on a labeled human/AI dataset |
| RQ5 | What are the computational trade-offs of adding explanation, behavioral verification, and adaptive fusion? | Latency/memory benchmarking, before/after each addition |
| RQ6 (new) | Does adaptive fusion, retrained on instructor feedback, measurably reduce false-positive rate over fixed weights? | Compare fixed-weight vs. retrained-weight performance on the same held-out set, over simulated feedback rounds |

RQ3 and RQ6 are the two most commonly skipped in comparable published work — do not treat either as optional.

---

## 4. Non-Goals (v1)

- Not multi-language (Python only; architecture must isolate language-specific preprocessing so this is extensible later)
- Not a graded/automated-penalty system — output is advisory only, always requires human judgment
- No user authentication/multi-tenancy — single-instructor local/small-deployment tool
- No LMS integration (Moodle/Canvas) in v1 — documented as future work only

---

## 5. Non-Negotiable Rules

1. **Zero cost, always.** No paid API keys, no paid hosting tier required for the core pipeline. See section 6 for the approved stack. If a task seems to need something paid, find the free/local equivalent or flag it — never silently add cost.
2. **Explainability contract (PRD's most important rule, carried forward):** No score of any kind — lexical, structural, semantic, behavioral, AI-generation-likelihood, or fused/overall — may reach the frontend without at least one traceable evidence item attached. A bare float or percentage with no evidence array is a spec violation, full stop.
3. **No unsandboxed execution of user-submitted code.** The behavioral module always runs through `subprocess` with a timeout and no network access — never `eval()`/`exec()`.
4. **Every module matches its interface exactly** (section 8) so modules stay independently swappable and testable.
5. **Adaptive fusion must be explainable too.** If/when fusion weights are retrained from feedback, the system must be able to state the *current* weights and *when* they were last updated — a self-adapting system that can't explain its own current state violates rule 2 at the meta level.
6. **Small, working increments.** Finish and review one module (with tests) before starting the next — see section 14.

---

## 6. Tech Stack (100% free/local)

| Layer | Choice | Notes |
|---|---|---|
| Frontend framework | **Next.js 16 + React 19 + TypeScript** | App Router; Vercel's native framework for zero-config free deployment |
| Styling | **Tailwind CSS v4** | Utility-first; see section 9 for the full design system |
| Charts | **Recharts** or **Chart.js** | For the analysis dashboard (score breakdowns, trend views) — pick one, Recharts recommended for React-native composition |
| Backend framework | **FastAPI (Python 3.11+)** | Async-native, Pydantic-validated, auto OpenAPI docs |
| ASGI server | **Uvicorn** | |
| ORM | **SQLAlchemy 2.0** | DB-agnostic — same code for SQLite and Postgres |
| Structural analysis | **Python `ast` (stdlib) + `zss`** | Zhang-Shasha tree edit distance; never hand-roll this |
| Semantic embeddings | **HuggingFace `transformers` + `torch`**, model: `microsoft/graphcodebert-base` (primary/eval) or `microsoft/unixcoder-base` (lighter, deployed) | Local CPU inference, no API calls |
| Adaptive fusion | **`scikit-learn` `LogisticRegression`** | Trained on `(lexical, structural, semantic, behavioral) → instructor_verdict` feature/label pairs |
| Behavioral sandbox | **Python `subprocess` + `resource` limits + `tempfile`** | No network access, strict timeout |
| AI-generation detection | **AST heuristics (v1) → optionally fine-tuned classifier (v2)**, informed by SemEval-2026 Task 13 methodology | Must produce feature-level evidence, not a bare probability |
| Database | **SQLite (local dev) / Supabase free-tier Postgres (deployed)** | Same schema, switched via `DATABASE_URL` env var |
| Report generation | **Jinja2 + WeasyPrint** | HTML → PDF, local rendering |
| Optional LLM explanation polish | **OpenRouter free-tier models (`:free` suffix) or local Ollama** | Never a dependency for any core score — polish only, on top of deterministic evidence |
| Deployment | **Vercel (frontend) + Render (backend) + Supabase (DB)** | All free tiers, no card required |
| Testing | **pytest (backend), Vitest/React Testing Library (frontend)** | |
| Formatting/linting | **`black` + `ruff` (Python), ESLint + Prettier (TS)** | |

---

## 7. Repository Structure (complete — fixes prior audit gaps)

```
ehsa/
├── INSTRUCTIONS.md                 # this file
├── README.md                        # quick start
├── AGENTS.md                        # AI-agent entry-point contract
├── docker-compose.yml               # one-command local run (build this — was missing before)
│
├── backend/
│   ├── requirements.txt             # pinned, deduplicated
│   ├── app/
│   │   ├── main.py                  # app factory, lifespan, CORS, router mount
│   │   ├── config.py                # FUSION_WEIGHTS default, MODEL_NAME, MAX_FILE_SIZE, timeouts — centralized, not scattered
│   │   ├── preprocessing/
│   │   │   ├── __init__.py
│   │   │   └── preprocess.py        # tokenize_code(), parse_ast() — NOT inline in routes.py
│   │   ├── similarity/
│   │   │   ├── lexical.py
│   │   │   ├── structural.py
│   │   │   ├── semantic.py
│   │   │   └── behavioral.py        # MUST be wired into the API route — see section 8.4
│   │   ├── fusion/
│   │   │   ├── fusion_engine.py     # supports both fixed-weight and learned-weight modes
│   │   │   └── adaptive_trainer.py  # retrains LogisticRegression from feedback table
│   │   ├── explain/
│   │   │   ├── transformation_detector.py
│   │   │   ├── explanation_generator.py
│   │   │   └── ai_generation_detector.py
│   │   ├── report/
│   │   │   └── report_generator.py  # JSON/HTML/PDF
│   │   ├── db/
│   │   │   ├── models.py            # Run, Evidence, Feedback, FusionWeightHistory (new)
│   │   │   └── session.py
│   │   └── api/
│   │       └── routes.py            # thin — orchestration only, no business logic inline
│   └── tests/
│       ├── fixtures/                # expand beyond 5 pairs — see section 13
│       └── test_*.py
│
├── frontend/
│   ├── package.json
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx             # upload + single comparison view
│       │   ├── dashboard/
│       │   │   └── page.tsx         # NEW — analysis dashboard, see section 9.4
│       │   ├── history/
│       │   │   └── page.tsx         # NEW — past runs list
│       │   └── batch/
│       │       └── page.tsx         # NEW — folder upload + similarity matrix
│       ├── components/
│       │   ├── UploadZone.tsx
│       │   ├── ScoreCard.tsx
│       │   ├── EvidencePanel.tsx    # NEW — renders matched n-grams, tree diff, cosine detail, behavioral table
│       │   ├── ExplanationBlock.tsx
│       │   ├── TransformationBadge.tsx
│       │   ├── ConfidenceIndicator.tsx  # NEW
│       │   ├── FeedbackButtons.tsx
│       │   ├── SimilarityMatrix.tsx     # NEW — batch mode heatmap
│       │   └── FusionWeightsPanel.tsx   # NEW — shows current adaptive weights + history
│       └── lib/
│           └── api.ts               # reads NEXT_PUBLIC_API_BASE_URL — never hardcode
│
├── experiments/
│   ├── evaluate.py
│   ├── results.csv
│   ├── review_log.csv
│   ├── instructor_study_guide.md
│   └── dataset/                     # expand to 30-50+ pairs minimum, plus a BigCloneBench subset
│
└── docs/
    ├── REFERENCES.md
    ├── DEPLOYMENT.md
    └── paper_draft.md
```

---

## 8. Module Specifications (exact interfaces)

### 8.1 Preprocessing
```python
# preprocessing/preprocess.py
def tokenize_code(code: str) -> list[str]: ...
def parse_ast(code: str) -> ast.AST | None:
    """Returns None on SyntaxError — callers must handle gracefully, never raise to the API layer."""
```

### 8.2 Lexical Similarity
```python
def lexical_similarity(tokens_a: list[str], tokens_b: list[str]) -> tuple[float, list[dict]]:
    """3-gram Jaccard. Evidence: top matched n-grams + counts."""
```

### 8.3 Structural Similarity
```python
def structural_similarity(ast_a: ast.AST | None, ast_b: ast.AST | None) -> tuple[float, list[dict]]:
    """ZSS tree edit distance, normalized. Evidence MUST include which subtrees matched/diverged —
    not just the aggregate distance (this was a known gap: fix it this time)."""
```

### 8.4 Semantic Similarity
```python
def semantic_similarity(code_a: str, code_b: str) -> tuple[float, list[dict]]:
    """GraphCodeBERT/UniXcoder cosine similarity, lazy-loaded model.
    Evidence: raw cosine value + a plain-language note on truncation if code exceeds 512 tokens
    (truncation must be disclosed as evidence, not silently applied)."""
```

### 8.5 Behavioral Similarity — MUST be wired into the API route, not left orphaned
```python
def behavioral_similarity(code_a: str, code_b: str, test_inputs: list[str]) -> tuple[float, list[dict]]:
    """Sandboxed subprocess execution, 2s timeout, no network access.
    Evidence: one item per test case — {input, output_a, output_b, matched}.
    If test_inputs is empty, auto-generate simple inputs from function signature where possible,
    else return (None, [{note: 'no test inputs available, behavioral signal skipped'}]) —
    never silently return 0.0, which would be indistinguishable from 'confirmed different'."""
```
This function's result MUST appear in `AnalyzeResponse` and MUST be included in `fuse()`'s input — verify this explicitly in the review pass (section 12), since this exact gap occurred in a prior build.

### 8.6 AI Generation Detector
```python
def detect_ai_generated(code: str) -> tuple[float, list[dict]]:
    """AST + statistical heuristics. Minimum feature set (expand beyond a prior 4-feature version):
    - docstring_density
    - type_hint_density
    - avg_identifier_length
    - naming_convention_compliance (snake_case/CONSTANT_CASE)
    - token_entropy (NEW — statistical diversity of token distribution)
    - comment_to_code_ratio (NEW)
    Evidence: one item per feature, each with {feature, value, interpretation}.
    A bare likelihood float with no evidence list is a spec violation."""
```

### 8.7 Fusion Engine — supports fixed AND adaptive modes
```python
# fusion/fusion_engine.py
def fuse(scores: dict, weights: dict | None = None) -> tuple[float, dict]:
    """scores = {lexical, structural, semantic, behavioral (nullable)}.
    If weights is None, load the CURRENT weights from config/DB (see adaptive_trainer.py) —
    defaults to a documented fixed starting point (e.g. 0.25 each, or 0.2/0.25/0.35/0.2 favoring
    semantic and behavioral) if no adaptive model has been trained yet.
    Returns (fused_score, weight_metadata) where weight_metadata states which weights were used
    and when they were last updated — required by Non-Negotiable Rule 5."""

# fusion/adaptive_trainer.py
def retrain_fusion_weights(db_session) -> dict:
    """Pulls all (run scores, feedback verdict) pairs from the DB, trains a LogisticRegression,
    extracts normalized coefficients as the new weights, persists them to a FusionWeightHistory
    table with a timestamp, returns the new weight dict. Should be callable on a schedule or
    manually triggered from an admin/dashboard action — document which in the actual implementation."""
```

### 8.8 Transformation Detector
```python
def detect_transformation(scores: dict, ai_likelihood: float) -> dict:
    """Returns {type, confidence, rule_matched}. Categories must include an explicit
    'likely_ai_rewrite' category fed by ai_likelihood — a prior version had an AI detector
    that never fed into the transformation categories at all. Fix that here."""
```

### 8.9 Explanation Generator
```python
def generate_explanation(scores: dict, transformation: dict, ai_evidence: list[dict]) -> str:
    """Template-based, deterministic. Must reference the actual score values passed in
    (not a generic sentence) and must incorporate AI-generation evidence into the text
    when relevant, not just the fusion/structural/lexical scores."""
```

---

## 9. UI / UX and Dashboard Specification

This section is deliberately detailed — a good dashboard is the difference between "a working pipeline" and "a tool an instructor actually trusts and uses."

### 9.1 Design System

- **Visual language:** dark, focused, "investigation tool" feel — not playful. Slate/near-black background, single accent color family (indigo/violet) for primary actions and scores, a second muted accent (amber) reserved *only* for flagged/high-similarity states, green reserved *only* for confirmed-safe/low-similarity states. Don't overload the palette — color should carry meaning, not decoration.
- **Typography:** one clean sans-serif for UI text (e.g. Geist, Inter), one monospace for all code snippets and evidence display (e.g. Geist Mono, JetBrains Mono) — code must never render in the UI sans-serif font.
- **Layout:** generous whitespace, evidence and scores never crammed — this is a tool for careful reading, not a glanceable summary.
- **Motion:** subtle only — score cards can fade/slide in on result arrival, no gratuitous animation. A tool making integrity-sensitive claims should feel calm and serious, not flashy.

### 9.2 Core comparison view (`/`)

Layered disclosure, in this exact order top to bottom — don't reorder:

1. **Upload zone** — two clearly labeled drop targets ("Submission" / "Reference"), `.py` only, drag-and-drop + click-to-browse, immediate filename confirmation on drop.
2. **One-line verdict** (appears first after analysis, largest text on the results screen) — e.g. "Likely variable renaming — 82% overall similarity, high confidence." This is the only thing many instructors will read; it must be self-sufficient and must be generated from `explanation_generator.py`, never a separate hardcoded string.
3. **Score cards row** — Fusion (large, primary), then Lexical / Structural / Semantic / Behavioral (secondary, equal visual weight to each other). Each card shows the percentage AND a small "view evidence" affordance that expands the `EvidencePanel` for that specific dimension — don't bury evidence behind a single generic "details" button; each score gets its own evidence trail.
4. **AI-Generation Likelihood card** — visually distinct from the four similarity cards (it's a different kind of claim), always paired with its feature-evidence list rendered inline or one click away, never just a bare percentage per Non-Negotiable Rule 2.
5. **Transformation type badge** — one of: Exact Copy / Variable Renaming / Structural Refactoring / Likely AI Rewrite / Partial Match / Unrelated. Each badge has a distinct color and icon, consistent across the whole app (reuse in history and batch views).
6. **Evidence panel (expandable per dimension)**
   - Lexical → side-by-side highlighted matching token n-grams
   - Structural → side-by-side AST subtree diff (which nodes matched, which diverged) — not just the raw edit-distance number
   - Semantic → the cosine value plus a plain note (e.g. "no truncation" or "file B truncated at 512 tokens — evidence is based on the first ~40 lines only")
   - Behavioral → a small table: input | output A | output B | matched (✓/✗), color-coded rows
7. **Fusion weights disclosure (small, collapsible, near the fusion score)** — states current weights and when they were last retrained (e.g. "Weights last updated 2026-07-20 from 34 instructor confirmations"). This is required by Non-Negotiable Rule 5, not optional polish.
8. **Instructor feedback** — two clear buttons, "Confirm Match" / "Mark False Positive," disabled during submission, with a confirmation toast on success. This feedback is what feeds section 8.7's retraining — say so in the UI copy, briefly, so instructors understand their feedback has real effect ("your feedback helps recalibrate future comparisons").

### 9.3 Confidence indicator (new component, not in prior builds)

Every score card gets a small secondary indicator — not just the percentage — showing whether the score is well-supported (e.g. based on substantial code, multiple matched evidence items) or thin (e.g. a very short file, truncated embedding, only one behavioral test case). Render as a simple 3-state marker (High / Medium / Low confidence) rather than a second number — instructors should not have to interpret two floats per card.

### 9.4 Analysis Dashboard (`/dashboard`) — new page, this is the "advanced" ask

This is a separate view from the single-comparison page — it's for reviewing patterns across many runs, not one pair.

- **Summary stat row:** total comparisons run, number flagged (above current threshold), average fusion score, current model/weight version.
- **Score distribution chart** — histogram of fusion scores across all runs, so an instructor can see where their class falls and where the flagged threshold sits visually.
- **Transformation type breakdown** — a simple bar or donut chart of how many runs fell into each transformation category.
- **Fusion weight drift chart** — a line chart showing how each of the four weights has moved over time as adaptive retraining has occurred (section 8.7). This is a genuinely novel visualization for this space — nobody else's tool shows its own fusion function evolving.
- **Feedback accuracy panel** — of the runs with instructor feedback, how often did "confirmed" align with a high fusion score and "false_positive" align with a low one — a simple calibration check rendered as a small scatter or confusion-style grid, directly supporting RQ2/RQ6 evidence-gathering, and giving the instructor a reason to trust the system's self-correction.
- **Recent runs table** — sortable by score/date/transformation type, linking into the full comparison view for any past run (requires the history/`GET /api/runs` endpoint — see section 10).

### 9.5 Batch mode (`/batch`)

- Multi-file upload (a whole folder/zip of submissions).
- Runs the full O(n²) pairwise comparison, showing a progress indicator (this can take a while — be honest about it in the UI, don't fake instant completion).
- Results render as a **similarity matrix heatmap** (`SimilarityMatrix.tsx`) — rows/columns are student files, cell color intensity is fusion score, click any cell to jump into the full single-comparison evidence view for that pair.
- A filter/threshold slider above the matrix lets the instructor adjust what counts as "flagged" live, re-coloring the heatmap without re-running analysis (client-side re-threshold against already-computed scores).

### 9.6 Accessibility and trust-specific UX notes

- Every score must have a text-equivalent for screen readers, not just a colored bar (e.g. `aria-label="Fusion similarity 82 percent, high confidence"`).
- Never round evidence-supporting numbers in a way that hides the actual computed value — the disclosure section can show full precision on hover/expand even if the card shows a rounded percentage.
- The explanation text should never use hedge-free absolute language ("this IS plagiarism") — always frame as investigative evidence ("this pattern is consistent with...") — this is both an accuracy issue and a due-process consideration explicitly noted in the project's own research framing.

---

## 10. API Contract

```
POST /api/v1/analyze
  body: { submission_code: str, reference_code: str, test_inputs?: list[str] }
  returns: {
    run_id, fusion_score, fusion_weight_metadata,
    components: { lexical, structural, semantic, behavioral (nullable),
                  lexical_evidence[], structural_evidence[], semantic_evidence[], behavioral_evidence[] },
    explanation: { transformation_type, confidence, human_readable },
    ai_generation: { likelihood, evidence[] },
    confidence_indicators: { lexical, structural, semantic, behavioral }
  }

POST /api/v1/feedback/{run_id}
  body: { verdict: "confirmed" | "false_positive" }   # Literal type, validated
  returns: { status: "ok" }

POST /api/v1/fusion/retrain
  returns: { new_weights, trained_on_n_samples, timestamp }
  # manual or scheduled trigger for adaptive_trainer.py

GET /api/v1/fusion/weights
  returns: { current_weights, last_updated, history: [...] }

POST /api/v1/compare/batch
  body: multipart form — files[]
  returns: { matrix: [[run_id, file_a, file_b, fusion_score, transformation_type], ...] }

GET /api/v1/runs?limit=50&sort=created_at
  returns: { runs: [...] }   # for the history page — did not exist in prior build, must exist now

GET /api/v1/report/{run_id}?format=json|html|pdf
  returns: report file

GET /api/v1/dashboard/summary
  returns: { total_runs, flagged_count, avg_fusion_score, score_distribution[],
             transformation_breakdown[], weight_drift_history[], calibration_data[] }
  # backs the /dashboard page directly

GET /health
  returns: { status: "ok" }
```

---

## 11. Database Schema

```sql
CREATE TABLE runs (
  id TEXT PRIMARY KEY,
  file_a_name TEXT, file_b_name TEXT,
  lexical_score REAL, structural_score REAL, semantic_score REAL, behavioral_score REAL,
  fusion_score REAL,
  fusion_weights_used TEXT,        -- JSON snapshot of weights at time of this run
  transformation_type TEXT, transformation_confidence REAL,
  ai_generation_likelihood REAL,
  explanation TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT REFERENCES runs(id),
  dimension TEXT,                   -- 'lexical' | 'structural' | 'semantic' | 'behavioral' | 'ai_generation'
  file_ref TEXT,                    -- 'a' or 'b', nullable for fused/ai evidence
  line_start INTEGER, line_end INTEGER,
  detail TEXT                       -- JSON blob of the evidence item — MUST actually be written, not just returned in API JSON (prior gap)
);

CREATE TABLE feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT REFERENCES runs(id),
  verdict TEXT CHECK(verdict IN ('confirmed','false_positive')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fusion_weight_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  weights TEXT,                     -- JSON: {lexical, structural, semantic, behavioral}
  trained_on_n_samples INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 12. Security Requirements

- File type validated server-side (not just `accept=".py"` on the frontend) — reject non-Python content even if the extension is spoofed.
- 1MB file size cap enforced in the Pydantic request validator.
- `feedback.verdict` validated as a `Literal` type, not a free string.
- CORS restricted to the actual deployed frontend origin in production — `allow_origins=["*"]` only acceptable for local dev.
- Behavioral sandbox: `subprocess` with `timeout`, `resource.setrlimit` for memory, and — document this as a known limitation if not fully implemented — ideally OS-level network namespace isolation; at minimum, disclose in `docs/DEPLOYMENT.md` that full network isolation is not guaranteed on free-tier hosting.
- No secrets/API keys in source — all via environment variables, `.env` gitignored.

---

## 13. Testing & Evaluation Requirements

- **Unit tests per module** — identical pair, unrelated pair, one realistic transformed pair, plus edge cases: empty file, syntax error, very short (1-line) file, very long (>512 token) file.
- **Benchmark dataset: minimum 30-50 hand-crafted pairs** across all transformation categories (exact copy, rename, structural refactor, AI-rewrite, unrelated) — five pairs, as used previously, is a smoke test, not an evaluation.
- **Real benchmark evaluation**, at minimum a labeled subset of BigCloneBench or OJClone, reporting Precision/Recall/F1/AUC-ROC against a human-labeled ground truth — this is required before any publication claim, not optional.
- **Ablation study, expanded from prior scope:**
  - lexical-only / structural-only / semantic-only / behavioral-only
  - fixed-weight fusion (all four) vs. adaptive/learned-weight fusion (RQ2, RQ6)
  - GraphCodeBERT vs. base CodeBERT (already partially done previously — keep and extend)
- **Instructor user study, real data** — minimum 5-8 participants, task-based (compare known pairs) + survey (explanation usefulness, 1-5 scale) + statistical comparison (Wilcoxon signed-rank, explanation-shown vs. score-only baseline condition).
- **Performance benchmarking** — latency/memory before and after adding each of: explanation generation, behavioral module, adaptive fusion — to directly answer RQ5.

---

## 14. Build Order (milestones)

| Phase | Deliverable |
|---|---|
| M1 | Preprocessing + Lexical + Structural modules, tested, with real subtree-diff evidence for structural |
| M2 | Semantic module (lazy-loaded) + fixed-weight Fusion engine |
| M3 | Transformation detector + explanation generator (referencing real scores in text) |
| M3.5 | AI-generation detector (6-feature version) — wired into transformation categories, not siloed |
| M4 | Behavioral module — built AND wired into `/analyze` from day one this time |
| M4.5 | Adaptive fusion: `adaptive_trainer.py`, `FusionWeightHistory` table, `/fusion/retrain` + `/fusion/weights` endpoints |
| M5 | Frontend: comparison view with full evidence panels, confidence indicators, fusion-weights disclosure (section 9.2, 9.3) |
| M6 | Analysis Dashboard page (section 9.4) + `/dashboard/summary` endpoint |
| M7 | Batch mode + similarity matrix heatmap (section 9.5) |
| M8 | History page + `/runs` endpoint + report export (JSON/HTML/PDF) |
| M9 | Expand benchmark dataset (30-50+ pairs) + BigCloneBench/OJClone subset evaluation + full ablation study |
| M10 | Instructor user study — real data collection and analysis |
| M11 | Security hardening pass (section 12) + deployment (Vercel + Render + Supabase) |
| M12 | Paper write-up |

Do not skip M4.5 or M10 under time pressure — these are the two milestones that differentiate this build from the prior version and from existing literature.

---

## 15. References (map every design decision to a citation when writing the paper)

- Feng et al. 2020 (CodeBERT) — evaluation baseline
- Guo et al. 2021 (GraphCodeBERT) — primary semantic model
- Karnalim et al. 2021 — closest explanation-oriented prior art; differentiate on multi-signal fusion
- Abid, Cai, Jiang 2023 — interpretability techniques informing evidence extraction
- Zhang & Saber 2025 (AST-Enhanced or AST-Overloaded?) — direct motivation for the behavioral module
- Martinez-Gil 2024-25 (ensemble similarity) — comparison baseline for fusion approach
- SemEval-2026 Task 13 — methodological basis for AI-generation detection
- A 2026 GraphCodeBERT+behavioral-feature paper — methodological basis for the behavioral module's evaluation design
- PAN 2025 plagiarism task findings — motivates why fusion (not semantic-only) generalizes better
- Low inter-tool-agreement study — motivates the evidence-first design principle generally

For the adaptive fusion contribution (section 8.7, this build's key addition): position it explicitly as extending Martinez-Gil's ensemble approach and FeatFuse's fusion-benchmarking infrastructure by closing the loop with real end-user feedback rather than a static or offline-only learned weighting — state clearly in the paper that this is the specific gap being filled.

---

## 16. Definition of Done (per module, non-negotiable)

A module is not done until:
- [ ] Matches the interface in section 8 exactly
- [ ] Returns evidence alongside every score, per Non-Negotiable Rule 2
- [ ] Has the full test set from section 13
- [ ] Evidence is actually persisted to the `evidence` table, not just returned in API JSON
- [ ] Logged in `experiments/review_log.csv` with the review checklist result (correctness, "is there a better way," cost audit, bug hunt, explainability audit)
- [ ] No paid API calls, no hardcoded secrets, nothing outside section 6's approved stack

A milestone is not done until every module in it passes the above, the full pipeline runs end-to-end on the fixture set without breaking a downstream module, and the zero-cost constraint has been re-verified across the whole stack, not just the new addition.
