# docs/ACTUAL_ARCHITECTURE.md — EHSA Reverse-Engineered Architecture

This document presents the reverse-engineered system architecture of EHSA (Explainable Hybrid Similarity Analyzer), derived strictly from the executable Python backend and Next.js frontend code.

---

## 1. Top-Level Architectural Overview

EHSA employs a decoupled client-server architecture with multi-signal similarity analysis, evidence-grounded explainability, and online adaptive feedback loops.

```mermaid
graph TD
    Client["Frontend UI (Next.js 16 + React 19)<br/>Monaco Editor / Recharts"]
    API["FastAPI App Server<br/>(app/main.py)"]
    Auth["Auth & Security Engine<br/>(PBKDF2 + JWT + RBAC)"]
    Orch["Analysis Orchestrator<br/>(app/api/routes.py)"]
    Pre["Preprocessing Module<br/>(app/preprocessing/preprocess.py)"]
    
    subgraph "Multi-Signal Similarity Pipeline"
        Lex["Lexical Analyzer<br/>(3-Gram Jaccard + difflib)"]
        Str["Structural Analyzer<br/>(AST ZSS Tree Edit Distance)"]
        Sem["Semantic Analyzer<br/>(UniXcoder 768d Embeddings)"]
        Beh["Behavioral Analyzer<br/>(Sandboxed Subprocess Execution)"]
    end
    
    subgraph "Explainability & AI Detection"
        Trans["Transformation Detector<br/>(AST Heuristic Classifier)"]
        AIDet["AI Generation Detector<br/>(6-Feature Entropy Model)"]
        Expl["Explanation Generator<br/>(Evidence Synthesizer)"]
    end
    
    subgraph "Adaptive Machine Learning"
        Fus["Fusion Engine<br/>(app/fusion/fusion_engine.py)"]
        Adapt["Adaptive Trainer<br/>(RidgeClassifier online retrainer)"]
    end
    
    DB[(SQLite / SQLAlchemy 2.0 Async<br/>users, runs, evidence, feedback)]

    Client -->|HTTP / JSON + Bearer JWT| API
    API --> Auth
    API --> Orch
    Orch --> Pre
    Pre --> Lex & Str & Sem & Beh
    Lex & Str & Sem & Beh --> Fus
    Lex & Str & Sem & Beh --> Trans & AIDet
    Trans & AIDet & Lex & Str & Sem & Beh --> Expl
    Fus --> Adapt
    Orch -->|Persist Runs & Evidence| DB
    Adapt -->|Persist Updated Weights| DB
    Client <--|Similarity Score + Evidence JSON| Orch
```

---

## 2. Component Technical Specification

### 2.1 Frontend Tier (`frontend/src/`)
- **Framework:** Next.js 16.2.11 (App Router) + React 19.2.4
- **Language:** TypeScript 5.0
- **Styling:** TailwindCSS v4 + `@tailwindcss/postcss`
- **Code Editor:** `@monaco-editor/react` v4.7.0
- **Data Visualization:** `recharts` v3.10.0
- **Icons:** `lucide-react` v1.26.0
- **HTTP Client:** `axios` v1.18.1 with `Authorization: Bearer <token>` interceptors.

### 2.2 Security & Authentication Tier (`backend/app/auth/`)
- **Password Hashing:** PBKDF2-HMAC-SHA256 with 100,000 iterations ([security.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/auth/security.py#L26-L35)).
- **JWT Authorization:** HS256 algorithm with 30-day token expiration ([security.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/auth/security.py#L42-L55)).
- **RBAC Roles:** `student`, `instructor`, `admin` enforced via `require_role(...)` ([dependencies.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/auth/dependencies.py#L69-L82)).
- **IDOR Protection:** `verify_run_access` dependency ensures students access only their own or unassigned guest runs, while instructors/admins access all runs ([dependencies.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/auth/dependencies.py#L85-L123)).

### 2.3 Preprocessing Module (`backend/app/preprocessing/preprocess.py`)
- **Input:** Raw Python source code string.
- **Operations:**
  1. AST canonicalization via `ast.parse` and `ast.unparse`.
  2. Comment and docstring removal via AST transformer nodes.
  3. Identifier extraction and token sequence normalization.
- **Output:** Cleaned source code, stripped AST representation, and raw token list.

### 2.4 Multi-Signal Similarity Pipeline (`backend/app/similarity/`)

#### Lexical Similarity ([lexical.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/similarity/lexical.py))
- **Method:** 3-gram multiset Jaccard similarity on Python token streams combined with `difflib.SequenceMatcher` line matching.
- **Formula:** $S_{\text{lex}} = 0.5 \cdot J_{3\text{-gram}}(T_A, T_B) + 0.5 \cdot \text{Ratio}_{\text{difflib}}(C_A, C_B)$
- **Output:** Score $\in [0, 1]$ and matching line token diffs.

#### Structural Similarity ([structural.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/similarity/structural.py))
- **Method:** Zhang-Shasha (ZSS) tree edit distance on simplified AST trees.
- **Formula:** $S_{\text{struct}} = 1.0 - \frac{\text{Distance}_{\text{ZSS}}(\text{AST}_A, \text{AST}_B)}{\max(|\text{AST}_A|, |\text{AST}_B|)}$
- **Output:** Score $\in [0, 1]$ and AST subtree insertion/deletion/substitution edit ops.

#### Semantic Similarity ([semantic.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/similarity/semantic.py))
- **Model:** `microsoft/unixcoder-base` (768-dimensional embedding space, 12 layers, 12 heads).
- **Pooling:** Mean pooling over non-padding token hidden states.
- **Formula:** $S_{\text{sem}} = \max\left(0, \frac{\mathbf{e}_A \cdot \mathbf{e}_B}{\|\mathbf{e}_A\|_2 \|\mathbf{e}_B\|_2}\right)$
- **Output:** Score $\in [0, 1]$ and 768d cosine distance.

#### Behavioral Similarity ([behavioral.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/similarity/behavioral.py))
- **Execution Mechanism:** Sandboxed `subprocess.Popen` with CPU timeout (2.0s limit) and memory limits (128MB cap).
- **Test Vectors:** 5 deterministic test inputs (integer, float, string, list, nested data).
- **Formula:** $S_{\text{beh}} = \frac{1}{K} \sum_{k=1}^K \text{Match}(\text{stdout}_A^{(k)}, \text{stdout}_B^{(k)})$
- **Output:** Score $\in [0, 1]$, output diffs, and execution status (`success`, `timeout`, `runtime_error`).

### 2.5 Explainability & AI Detection (`backend/app/explain/`)

#### Transformation Classifier ([transformation_detector.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/explain/transformation_detector.py))
- Evaluates AST structural divergence against lexical similarity to classify code transformation techniques into 7 distinct categories: `unmodified_copy`, `variable_renaming`, `statement_reordering`, `control_flow_mutation`, `dead_code_injection`, `ai_assisted_rewrite`, and `structural_refactoring`.

#### AI Generation Detector ([ai_generation_detector.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/explain/ai_generation_detector.py))
- Computes 6 code quality metrics: docstring density, type hint density, average identifier length, PEP8 naming compliance, token Shannon entropy, and comment-to-code ratio.
- Outputs an AI likelihood score $\in [0, 1]$ and identified zero-shot LLM code traits.

#### Explanation Generator ([explanation_generator.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/explain/explanation_generator.py))
- Synthesizes all 4 similarity scores, AST edit operations, token diffs, behavioral trace outputs, and AI detector features into human-readable evidence summaries for instructors.

### 2.6 Adaptive Fusion Engine (`backend/app/fusion/`)
- **Default Weights:** Lexical = 0.25, Structural = 0.30, Semantic = 0.30, Behavioral = 0.15 ([fusion_engine.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/fusion/fusion_engine.py#L32-L37)).
- **Adaptive Retraining:** `RidgeClassifier` fits on instructor feedback labels (`confirmed` = 1 vs `false_positive` = 0). Coefficients are normalized via softmax/min-max to ensure $\sum w_i = 1.0$ and non-negativity ([adaptive_trainer.py](file:///d:/Projects/EHSA%20%E2%80%94%20Explainable%20Hybrid%20Similarity%20Analyzer/backend/app/fusion/adaptive_trainer.py#L45-L95)).

---

## 3. Data Flow Diagram

```mermaid
sequenceDocument
sequenceDiagram
    autonumber
    actor User as Client UI / Instructor
    participant API as FastAPI Router (/analyze)
    participant Pre as Preprocessor
    participant Pipe as Similarity Pipeline (Lex/Struct/Sem/Beh)
    participant AIDet as AI & Transformation Detector
    participant Fus as Fusion Engine
    participant Expl as Explanation Generator
    participant DB as SQLite Database

    User->>API: POST /api/v1/analyze (code_a, code_b)
    API->>Pre: Canonicalize AST & remove comments
    Pre-->>API: Cleaned AST & tokens
    
    par Parallel Metric Evaluation
        API->>Pipe: Run Lexical Similarity (3-gram)
        API->>Pipe: Run Structural Similarity (ZSS AST)
        API->>Pipe: Run Semantic Similarity (UniXcoder)
        API->>Pipe: Run Sandboxed Behavioral Execution
    end
    Pipe-->>API: Metric scores & evidence blobs
    
    API->>AIDet: Analyze 6 LLM features & AST transformations
    AIDet-->>API: AI score & transformation label
    
    API->>Fus: Fuse metrics (current weights w_i)
    Fus-->>API: Composite score & classification verdict
    
    API->>Expl: Synthesize multi-signal evidence
    Expl-->>API: Natural language explanation
    
    API->>DB: Save Run & Evidence record
    DB-->>API: Persisted run_id
    
```

---

## 7. Sandbox Security Boundary & Isolation Architecture

> [!CAUTION]
> **Production Security Notice:** The in-process AST pre-checker (`_check_blocked_imports`) and subprocess resource limits (`resource.setrlimit`, `BEHAVIORAL_TIMEOUT_SECONDS`) in `app/similarity/behavioral.py` form a **defense-in-depth prototype only**. Blocklists in Python cannot guarantee absolute isolation against all arbitrary code execution vectors. 

### Recommended Production Deployment Model
For multi-tenant or untrusted student code execution, production environments **MUST** execute the behavioral analysis engine inside an isolated container sandbox:
1. **Container Isolation:** Run worker processes inside an unprivileged Docker / OCI container or `nsjail` / `gVisor` sandbox.
2. **Network Disabling:** `--network none` (disable all egress/ingress networking).
3. **Filesystem Isolation:** Read-only root filesystem with temporary `tmpfs` mounts.
4. **Kernel Security Filters:** Apply `seccomp` profile blocking `ptrace`, `kexec_load`, and socket creation syscalls.
