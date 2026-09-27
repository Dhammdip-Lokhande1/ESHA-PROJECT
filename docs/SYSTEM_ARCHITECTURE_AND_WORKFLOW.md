# EHSA — System Architecture & Complete Workflow Diagrams

This document contains the complete, reverse-engineered **System Architecture Diagrams** and **Sequence Workflows** for **EHSA — Explainable Hybrid Similarity Analyzer**, formatted in high-fidelity Mermaid syntax matching production architecture specifications.

---

# 1. System Block Architecture Diagram

```mermaid
graph TD
    subgraph Frontend["Next.js 16 Client - Port 3000"]
        FE_Editor["Dual Monaco Editor / Pairwise UI (page.tsx)"]
        FE_Batch["Batch Comparison Matrix UI (batch/page.tsx)"]
        FE_Dash["Instructor Calibration Dashboard (instructor/page.tsx)"]
        FE_Auth["AuthProvider React Context (lib/auth.tsx)"]
        FE_Axios["Axios API Client Interceptor (lib/api.ts)"]

        FE_Editor --> FE_Axios
        FE_Batch --> FE_Axios
        FE_Dash --> FE_Axios
        FE_Auth --> FE_Axios
    end

    FE_Axios -- "POST /api/v1/analyze" --> API_Router
    FE_Axios -- "POST /api/v1/compare/batch" --> API_Router
    FE_Axios -- "POST /api/v1/feedback/{id}" --> API_Router
    FE_Axios -- "POST /api/v1/fusion/retrain" --> API_Router
    FE_Axios -- "GET /api/v1/report/{id}" --> API_Router

    subgraph Backend["FastAPI Engine - Port 8000"]
        API_Router["APIRouter Layer (app.api.routes)"]
        RateLimiter["SlidingWindowRateLimiter (rate_limiter.py)"]
        AuthDep["JWT & Role Guard (dependencies.py)"]
        Prep_Engine["PreprocessingEngine - Tokenizer & AST Parser (preprocess.py)"]
        ParallelGather["asyncio.gather ThreadPool Orchestrator"]
        
        API_Router --> RateLimiter
        RateLimiter --> AuthDep
        AuthDep --> Prep_Engine
        Prep_Engine --> ParallelGather

        subgraph CorePipelines["Multi-Channel Similarity Pipelines"]
            Lex_Module["LexicalScorer - 3-Gram Multiset Jaccard (lexical.py)"]
            Struct_Module["StructuralScorer - Zhang-Shasha AST Edit Distance (structural.py)"]
            Sem_Module["SemanticScorer - UniXcoder Mean-Pooled Cosine (semantic.py)"]
            Beh_Module["BehavioralSandbox - Subprocess Timeout & 128MB Cap (behavioral.py)"]
            AI_Module["AIGenerationDetector - 6 Feature Heuristics (ai_generation_detector.py)"]
        end

        ParallelGather --> Lex_Module
        ParallelGather --> Struct_Module
        ParallelGather --> Sem_Module
        ParallelGather --> Beh_Module
        ParallelGather --> AI_Module

        subgraph ReasoningEngine["Adaptive Fusion & Explanation Engine"]
            Fusion_Module["AdaptiveFusionEngine - Renormalized Weights (fusion_engine.py)"]
            Trainer_Module["AdaptiveTrainer - LogisticRegression (adaptive_trainer.py)"]
            Class_Module["TransformationClassifier - 6-Rule Hierarchy (transformation_detector.py)"]
            Expl_Module["ExplanationGenerator - Deterministic Verdict & Narrative (explanation_generator.py)"]
            Conf_Module["ConfidenceCalculator - High/Med/Low Status (confidence.py)"]
        end

        Lex_Module --> Fusion_Module
        Struct_Module --> Fusion_Module
        Sem_Module --> Fusion_Module
        Beh_Module --> Fusion_Module
        
        Fusion_Module --> Class_Module
        AI_Module --> Class_Module
        Class_Module --> Expl_Module
        Expl_Module --> Conf_Module

        DB_ORM["SQLAlchemy 2.0 Async Session (session.py)"]
        DB_SQLite[("SQLite - ehsa.db")]

        Conf_Module --> DB_ORM
        Trainer_Module --> DB_ORM
        DB_ORM --> DB_SQLite
    end

    subgraph StorageCache["Local Storage & Cache"]
        Model_Cache["huggingface_cache/ microsoft/unixcoder-base"]
        Reports_Dir["exports/ JSON, HTML & PDF Export Reports"]
    end

    Sem_Module --> Model_Cache
    API_Router --> Reports_Dir
```

---

# 2. Complete End-to-End Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Instructor
    participant FE as Next.js 16 Frontend
    participant API as FastAPI Backend (routes.py)
    participant Auth as Auth & Rate Limiter
    participant Core as Parallel Similarity Pipelines
    participant Model as PyTorch / UniXcoder Cache
    participant DB as SQLite Database (ehsa.db)

    User->>FE: Input/Paste Python Code Pair (Submission.py, Reference.py)
    FE->>API: POST /api/v1/analyze (JSON Body + Bearer JWT Header)
    
    API->>Auth: Check Sliding Window Rate Limit (max 30 req/min)
    Auth-->>API: Rate Limit OK
    API->>Auth: Resolve Authorization Bearer Token & User Context
    Auth-->>API: User Context (student/instructor/admin or guest)

    API->>Core: Preprocess Code: Tokenize (tokenize_code) & Parse AST (ast.parse)
    
    par Parallel Pipeline Execution (asyncio.gather)
        Core->>Core: 1. Lexical 3-Gram Multiset Jaccard (lexical_similarity)
        Core->>Core: 2. Structural Zhang-Shasha AST Edit Distance (structural_similarity)
        Core->>Model: 3. Semantic UniXcoder Embedding Mean-Pooling (semantic_similarity)
        Model-->>Core: Cosine Similarity Vector Float
        Core->>Core: 4. Behavioral Subprocess Sandbox Execution (2.0s timeout, 128MB cap)
        Core->>Core: 5. AI Generation Heuristic Detector (6 Features)
    end

    Core-->>API: Return Raw Channel Scores & Detailed Evidence Arrays

    API->>Core: fuse(scores, weights) — Exclude None signals & Renormalize Weights
    Core-->>API: Fused Composite Score & Weight Metadata

    API->>Core: detect_transformation(scores, ai_likelihood)
    Note over Core: Evaluate Rule Hierarchy: AI Rewrite (>=0.65) -> Exact Copy -> Renaming -> Refactoring -> Partial -> Unrelated
    Core-->>API: Transformation Type & Rule Confidence

    API->>Core: generate_explanation() & compute_confidence_indicators()
    Core-->>API: Structured Verdict, Narrative Paragraph & Confidence Status

    rect rgb(30, 41, 59)
        Note over API, DB: Async Database Transaction (SQLAlchemy 2.0)
        API->>DB: INSERT INTO runs (id, user_id, scores, transformation_type, explanation)
        API->>DB: Bulk INSERT INTO evidence (run_id, dimension, line_refs, detail JSON)
        DB-->>API: Transaction Committed
    end

    API-->>FE: Return 200 OK AnalyzeResponse JSON
    FE-->>User: Render ScoreCard Gauges, Evidence Highlights & Verdict Block

    opt Instructor Verdict Submission & Adaptive Weight Retraining
        User->>FE: Click "Confirm Plagiarism" or "False Positive"
        FE->>API: POST /api/v1/feedback/{run_id} (verdict="confirmed")
        API->>DB: INSERT INTO feedback (run_id, user_id, verdict)
        DB-->>API: Feedback Saved
        API-->>FE: 200 OK {status: "ok"}

        User->>FE: Click "Retrain Fusion Weights" (Instructor Dashboard)
        FE->>API: POST /api/v1/fusion/retrain
        API->>DB: SELECT Runs & Feedback Records
        DB-->>API: Feedback Dataset (Features X, Labels y)
        API->>Core: Fit Scikit-learn Logistic Regression Model & Normalize Positive Weights
        API->>DB: INSERT INTO fusion_weight_history (weights, trained_on_n_samples)
        DB-->>API: Weights Persisted
        API-->>FE: Return Updated Effective Weights & Historical Drift Data
    end
```

---

# 3. Batch Comparison Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Instructor
    participant FE as Batch Page (batch/page.tsx)
    participant API as API Router (routes.py)
    participant Core as Core Analysis Engine
    participant DB as SQLite Database

    User->>FE: Select 2 to 20 Python Files & Click "Run Batch Comparison"
    FE->>API: POST /api/v1/compare/batch (Multipart Form Data)
    API->>API: Validate File Count (2 <= N <= 20) & File Sizes (<= 1MB)
    
    loop Every Unique Code Pair (i, j) for O(n²) Comparisons
        API->>Core: Invoke analyze(file_i, file_j)
        Core->>DB: Persist Pairwise Run & Evidence Rows
        Core-->>API: Pair AnalyzeResponse JSON
    end

    API-->>FE: Return Aggregated Similarity Matrix JSON
    FE-->>User: Render Interactive N x N Heatmap Matrix
```

---

# 4. User Authentication & Authorization Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student / User
    participant FE as Register / Login UI
    participant API as Auth Routes (auth_routes.py)
    participant Sec as Cryptographic Security (security.py)
    participant DB as SQLite Database

    Student->>FE: Input Username, Email, Password & Click Register
    FE->>API: POST /api/v1/auth/register
    API->>Sec: hash_password(password) via PBKDF2-HMAC-SHA256
    Sec-->>API: Salted Hash String (100k iterations)
    API->>DB: INSERT INTO users (role="student", is_active=1)
    DB-->>API: User Created
    API-->>FE: 201 Created (User Profile JSON)

    Student->>FE: Input Credentials & Click Login
    FE->>API: POST /api/v1/auth/login
    API->>DB: SELECT User WHERE username OR email
    DB-->>API: Stored User Record
    API->>Sec: verify_password(plain_password, password_hash)
    Sec-->>API: Password Valid (True)
    API->>Sec: create_access_token(user_id, role)
    Sec-->>API: HS256 JWT Token String
    API-->>FE: Return LoginResponse (access_token + User)
    FE->>FE: Save JWT to localStorage ("ehsa_auth_token")
```

---

# 5. Database ER Diagram

```mermaid
erDiagram
    users ||--o{ runs : "initiates / owns"
    users ||--o{ feedback : "submits"
    runs ||--o{ evidence : "contains (1-to-N cascade)"
    runs ||--o{ feedback : "receives (1-to-N cascade)"
    fusion_weight_history {
        int id PK
        string weights JSON
        int trained_on_n_samples
        datetime created_at
    }

    users {
        string id PK "UUID"
        string username UK
        string email UK
        string password_hash
        string role "student|instructor|admin"
        int is_active
        datetime created_at
        datetime updated_at
    }

    runs {
        string id PK "UUID"
        string user_id FK "nullable"
        string file_a_name
        string file_b_name
        float lexical_score
        float structural_score
        float semantic_score
        float behavioral_score
        float fusion_score
        string fusion_weights_used "JSON"
        string transformation_type
        float transformation_confidence
        float ai_generation_likelihood
        string explanation "JSON"
        datetime created_at
    }

    evidence {
        int id PK "autoincrement"
        string run_id FK
        string dimension
        string file_ref
        int line_start
        int line_end
        string detail "JSON"
    }

    feedback {
        int id PK "autoincrement"
        string run_id FK
        string user_id FK
        string verdict "confirmed|false_positive"
        datetime created_at
    }
```
