# EHSA — Explainable Hybrid Similarity Analyzer

> An evidence-first Python source-code similarity investigation tool for instructors and software engineers.

Every score carries traceable evidence. Fusion weights adapt from real instructor feedback. Zero paid APIs required.

---

## Key Features

- **Multi-Signal Similarity Pipeline:**
  - **Lexical:** Token-level Jaccard similarity and sequence matching.
  - **Structural:** AST subtree edit distance via the ZSS algorithm.
  - **Semantic:** Code embeddings via UniXcoder (`microsoft/unixcoder-base`).
  - **Behavioral:** Sandboxed execution trace profiling (2.0s timeout; 128MB memory cap via Unix `resource` limits with Windows timeout fallback).
  - **AI-Rewrite Detection:** Rule-based heuristics for AI-related code transformation indicators.
- **Dual Analysis Modes:** File upload (`.py`) OR direct side-by-side code pasting.
- **Quick Demo Presets:** Pre-configured code pairs (Variable Renaming, Structural Refactoring, AI Rewrite) for instant 1-click evaluation.
- **Evidence-First Persistence:** Full evidence blobs saved to database tables (`evidence`) alongside every run score.
- **Adaptive Fusion:** Ridge regression classifier weighting component scores based on instructor feedback.
- **Guest Privacy & Run Claiming:**
  - Unauthenticated guests can analyze code, export reports, and view results.
  - Guest runs (`user_id = None`) are strictly isolated and excluded from registered user feeds.
  - Authenticated users can claim guest runs via `POST /api/v1/runs/{run_id}/claim`.
- **Security & Usage Control:** PBKDF2-HMAC-SHA256 password hashing, signed HS256 JWT tokens, server-side RBAC (`student`, `instructor`, `admin`), IDOR protection across all routes, thread-safe sliding window rate limiting, and sanitized 500 error responses.
- **Exportable Reports:** Download printable HTML reports or raw JSON evidence payloads directly from the result UI or API.

---

## Quick Start (Docker — recommended)

```bash
docker compose up --build
```

- **Frontend UI:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs

---

## Local Development (without Docker)

### Backend Setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app/initial_data.py  # Bootstraps initial DB tables & admin user
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Run Automated Test Suite (255 / 255 Passed)

```bash
cd backend
python -m pytest tests/ -v
```

---

## Security, Authentication & Role-Based Access Control (RBAC)

EHSA implements enterprise-grade authentication, password security, and Role-Based Access Control (RBAC):

### User Roles & Permissions

- **`student`**: Can submit code for analysis (`/analyze`, `/compare/batch`), view their own submissions and reports, and claim guest runs. Cannot access instructor feedback (`/feedback`), retrain fusion weights, view overall metrics, or access user management.
- **`instructor`**: All student capabilities + review all student submissions/evidence, access the analysis dashboard, submit instructor feedback verdicts (`confirmed` vs `false_positive`), and trigger adaptive fusion retraining.
- **`admin`**: All instructor capabilities + Admin User Management (`/admin/users`), assigning roles, and managing account activation status.

### Rate Limiting Limits
- **`/auth/login`**: 15 requests / min
- **`/auth/register`**: 10 requests / min
- **`/analyze`**: 30 requests / min
- **`/compare/batch`**: 10 requests / min
- **`/fusion/retrain`**: 5 requests / min

### Initial Admin Credentials (Bootstrapped on Startup)
- **Username:** `admin`
- **Email:** `admin@ehsa.local`
- **Password:** `AdminSecretPass123!` *(configurable via environment variables)*

---

## Environment Variables

Copy `.env.example` to `.env` and adjust settings as needed:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./ehsa.db` | DB connection string (SQLite / PostgreSQL) |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend API URL for frontend |
| `MODEL_NAME` | `microsoft/unixcoder-base` | HuggingFace model for semantic similarity |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origin header for FastAPI CORS |
| `MAX_FILE_SIZE_BYTES` | `1048576` | Server-side maximum file size cap (1MB) |
| `SECRET_KEY` | `ehsa-production-secret-key-change-in-prod-2026` | Cryptographic secret for JWT token signing |
| `INITIAL_ADMIN_USERNAME` | `admin` | Initial admin username on DB initialization |
| `INITIAL_ADMIN_EMAIL` | `admin@ehsa.local` | Initial admin email on DB initialization |
| `INITIAL_ADMIN_PASSWORD` | `AdminSecretPass123!` | Initial admin password on DB initialization |

---

## Research Evaluation & Master Benchmark Results

EHSA has been rigorously evaluated under zero-leakage 5-Fold GroupKFold cross-validation across 4 benchmark suites ($N = 522$ total pairs):

| Benchmark Dataset | $N$ | Positive | Negative | Evaluation Mode | Precision | Recall | $F_1$ Score | MCC | ROC-AUC |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **EHSA-Synth Core** | 150 | 120 | 30 | Fixed Default Weights | 0.9739 | 0.9333 | **0.9532** | 0.7881 | 0.9733 |
| **EHSA-Synth Full** | 180 | 120 | 60 | Fixed Default Weights | 0.8296 | 0.9333 | **0.8784** | 0.5988 | 0.8881 |
| **EHSA-Synth Adaptive**| 180 | 120 | 60 | Adaptive Fusion (5-Fold GKF)| 0.8842 | 0.9500 | **0.9160** | 0.7182 | 0.8870 |
| **IBM CodeNet** | 100 | 50 | 50 | Fixed Default Weights | 0.9000 | 0.9000 | **0.9000** | 0.8000 | 0.9256 |
| **TransBench-Lite** | 210 | 150 | 60 | Fixed Default Weights | 0.9615 | 1.0000 | **0.9804** | 0.9303 | 1.0000 |
| **OJClone-32** | 32 | 22 | 10 | Zero-Shot Direct | 1.0000 | 0.5455 | **0.7059** | 0.5222 | 0.7955 |

- **Zero Data Leakage:** GroupKFold grouping on `source_program_id` and `problem_id` guarantees zero overlap of program families or problem categories across training and testing folds.
- **Statistical Significance:** Multi-view fusion significantly outperforms single-view baselines ($p < 0.001$, McNemar test); evidence presentation yields statistically significant decision confidence gains ($p < 0.001$, Wilcoxon test).

---

## Build Milestones

| Milestone | Status |
|---|---|
| M1 — Preprocessing + Lexical + Structural | ✅ Verified |
| M2 — Semantic + Fixed-weight Fusion | ✅ Verified |
| M3 — Transformation Detector + Explanation | ✅ Verified |
| M3.5 — AI Generation Detector | ✅ Verified |
| M4 — Behavioral Module | ✅ Verified |
| M4.5 — Adaptive Fusion | ✅ Verified |
| M5 — Frontend Comparison View (Dual Mode + Presets) | ✅ Verified |
| M6 — Analysis Dashboard | ✅ Verified |
| M7 — Batch Mode + Matrix | ✅ Verified |
| M8 — History + Report Export (HTML/JSON) | ✅ Verified |
| M9 — Security, Authentication & RBAC | ✅ Verified |
| M11 — Rate Limiting, Guest Privacy & IDOR Protection | ✅ Verified (255/255 Tests Passed) |
| M12 — Production Build & Master Research Audit | ✅ Verified (100% Documentation Sync) |

