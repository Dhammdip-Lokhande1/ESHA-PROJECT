# EHSA — Research-Grade Architecture & Workflow Diagrams

This document contains the complete, publication-grade diagram set for **EHSA — Explainable Hybrid Similarity Analyzer**, designed for inclusion in research papers, the **IFGSCET-2026 conference presentation**, master/doctoral theses, live demonstrations, and technical documentation.

---

# Figure 1: EHSA High-Level System Architecture

### Suitability
- **Primary Use**: Thesis Architecture Chapter, Technical Documentation, System Overview Slide
- **Target Audience**: Conference Reviewers, System Architects, Technical Evaluators

```mermaid
flowchart LR
    subgraph Users["Layer 1: Users"]
        GuestUser["Guest User"]
        StudentUser["Student User"]
        InstructorUser["Instructor"]
        AdminUser["Administrator"]
    end

    subgraph Frontend["Layer 2: Web Interface (Next.js 16 + React 19)"]
        MonacoUI["Dual Monaco Code Editor"]
        DashUI["Student & Instructor Dashboards"]
        BatchUI["O(n²) Batch Comparison UI"]
        HistoryUI["Investigation History Browser"]
    end

    subgraph API_Layer["Layer 3: API & Security Gateway (FastAPI)"]
        APIGateway["FastAPI Gateway"]
        AuthSec["PBKDF2 Auth & JWT Resolver"]
        RBACGuard["RBAC & Ownership Guard"]
        RateLimit["Sliding-Window Rate Limiter"]
    end

    subgraph AnalysisEngine["Layer 4: Multi-View Analysis Engine"]
        Prep["AST Parser & Tokenizer"]
        Lexical["Lexical Scorer (3-Gram Jaccard)"]
        Structural["Structural Scorer (Zhang-Shasha AST)"]
        Semantic["Semantic Scorer (UniXcoder Cosine)"]
        Behavioral["Behavioral Sandbox (Subprocess Cap)"]
        AIDetector["AI Generator Detector (AST Heuristics)"]
    end

    subgraph IntelligenceLayer["Layer 5: Intelligence & Explanation Engine"]
        EvidenceAgg["Evidence Aggregator"]
        AdaptiveFusion["Adaptive Fusion (Renormalized Weights)"]
        TransformationClass["Transformation Classifier (6 Rules)"]
        ExplanationEng["Deterministic Narrative Generator"]
    end

    subgraph StorageLayer["Layer 6: Persistence Layer (SQLite + SQLAlchemy 2.0)"]
        DB_Users[("users Table")]
        DB_Runs[("runs Table")]
        DB_Evidence[("evidence Table")]
        DB_Feedback[("feedback Table")]
        DB_History[("fusion_weight_history Table")]
    end

    subgraph ResearchPipeline["Layer 7: Offline Research & Benchmark Pipeline"]
        BenchData["150-Pair Research Benchmark"]
        GroupedCV["5-Fold Grouped Stratified CV"]
        AblationEngine["Ablation & Metrics Engine"]
    end

    Users --> Frontend
    Frontend -- "HTTP / REST (Axios)" --> API_Layer
    API_Layer --> AnalysisEngine
    
    Prep --> Lexical
    Prep --> Structural
    Prep --> Semantic
    Prep --> Behavioral
    Prep --> AIDetector

    Lexical --> EvidenceAgg
    Structural --> EvidenceAgg
    Semantic --> EvidenceAgg
    Behavioral --> EvidenceAgg
    AIDetector --> TransformationClass

    EvidenceAgg --> AdaptiveFusion
    AdaptiveFusion --> TransformationClass
    TransformationClass --> ExplanationEng

    ExplanationEng --> StorageLayer
    DB_Users -.-> AuthSec
    DB_Runs -.-> HistoryUI
    DB_Feedback -.-> AdaptiveFusion

    BenchData --> GroupedCV
    GroupedCV --> AnalysisEngine
    AnalysisEngine --> AblationEngine
```

### Explanation & Components Represented
- **Layer 1 (Users)**: Guest, Student, Instructor, and Admin roles interacting via explicit permissions.
- **Layer 2 (Frontend)**: Next.js 16 App Router UI containing Monaco Editor, Dashboard, Batch matrix, and History browser.
- **Layer 3 (API & Security)**: FastAPI gateway protected by PBKDF2 authentication, JWT tokens, RBAC guards, and sliding-window rate limiting.
- **Layer 4 (Analysis Engine)**: Preprocessing, Lexical (3-gram Jaccard), Structural (Zhang-Shasha AST edit distance), Semantic (UniXcoder cosine), Behavioral sandbox (128MB/2.0s limit), and AI generation detector.
- **Layer 5 (Intelligence)**: Evidence aggregation, adaptive weight fusion, 6-category transformation classification, and deterministic explanation generation.
- **Layer 6 (Persistence)**: SQLite database (`ehsa.db`) containing `users`, `runs`, `evidence`, `feedback`, and `fusion_weight_history` tables.
- **Layer 7 (Research)**: Decoupled 150-pair benchmark evaluation pipeline running 5-fold grouped cross-validation independently from production execution.

---

# Figure 2: EHSA End-to-End Similarity Analysis Workflow

### Suitability
- **Primary Use**: Technical Documentation, Implementation Walkthrough, Developer Onboarding
- **Target Audience**: Software Engineers, Code Reviewers

```mermaid
flowchart TD
    Start([START: User Submits Source Code Pair]) --> FE_Val[Frontend Input & File Size Validation]
    FE_Val --> HTTP_Req[POST /api/v1/analyze with Authorization Header]
    HTTP_Req --> API_Val[Backend Payload & Schema Validation]
    API_Val --> Rate_Check{Rate Limit Check}
    
    Rate_Check -- Exceeded --> Err429[429 Too Many Requests]
    Rate_Check -- Allowed --> Auth_Resolve[Resolve JWT User Context or Guest Session]
    
    Auth_Resolve --> Preprocess[Tokenize Code & Parse AST Trees]
    
    subgraph ParallelEngine["Parallel Multi-View Execution (asyncio.gather)"]
        Preprocess --> Lex_Run[Lexical 3-Gram Multiset Jaccard]
        Preprocess --> Struct_Run[Structural Zhang-Shasha AST Edit Distance]
        Preprocess --> Sem_Run[Semantic UniXcoder Mean-Pooled Cosine]
        Preprocess --> Beh_Run[Behavioral Subprocess Sandbox Execution]
        Preprocess --> AI_Run[AI Generation Heuristic Detector]
    end

    Lex_Run --> Ev_Collect[Aggregate Raw Channel Evidence Items]
    Struct_Run --> Ev_Collect
    Sem_Run --> Ev_Collect
    Beh_Run --> Ev_Collect
    AI_Run --> Ev_Collect

    Ev_Collect --> Weight_Renorm[Load Weights & Renormalize Excluded Signals]
    Weight_Renorm --> Fuse_Score[Calculate Fused Similarity Score]
    Fuse_Score --> Trans_Class[Classify Transformation Type & Confidence]
    Trans_Class --> Expl_Gen[Generate Verdict String, Narrative & Caveats]
    Expl_Gen --> Conf_Calc[Compute High/Medium/Low Confidence Indicators]

    Conf_Calc --> DB_Save[(Persist Run & Evidence Rows to SQLite)]
    DB_Save --> Resp_JSON[Return AnalyzeResponse JSON Payload]
    Resp_JSON --> UI_Render[Render ScoreCard, Evidence Panel & Verdict]
    UI_Render --> End([END: User Investigates Grounded Evidence])
```

### Explanation & Components Represented
Traces the runtime execution path of a pairwise analysis request from client input to database storage and visual disclosure. Demonstrates how preprocessing, parallel feature channels, weight renormalization, transformation classification, narrative generation, and confidence calculations coordinate sequentially.

---

# Figure 3: EHSA Multi-View Similarity Analysis Pipeline

### Suitability
- **Primary Use**: Research Paper Method Methodology Section, Conference Slide (Pipeline)
- **Target Audience**: Computer Science Researchers, AI & Software Engineering Reviewers

```mermaid
flowchart TD
    Pair[SOURCE CODE PAIR: Code A & Code B] --> Prep[AST Parsing & Tokenization]

    subgraph Views["Multi-Channel Feature Extraction"]
        Prep --> Lexical["Lexical Channel<br/><i>3-Gram Multiset Jaccard</i>"]
        Prep --> Structural["Structural Channel<br/><i>AST + Zhang-Shasha Distance</i>"]
        Prep --> Semantic["Semantic Channel<br/><i>UniXcoder Embedding Cosine</i>"]
        Prep --> Behavioral["Behavioral Channel<br/><i>Resource-Limited Execution</i>"]
        Prep --> AISignal["AI Generation Detector<br/><i>AST + Lexical Heuristics</i>"]
    end

    Lexical --> RawEvidence[Raw Traceable Evidence Arrays]
    Structural --> RawEvidence
    Semantic --> RawEvidence
    Behavioral --> RawEvidence
    AISignal --> RawEvidence

    RawEvidence --> EvidenceFusion[Signal Renormalization & Weight Fusion]
    EvidenceFusion --> FinalResult[Final Grounded Analysis & Classification]
```

### Explanation & Components Represented
Focuses exclusively on the core multi-channel similarity engine. Highlights the five distinct extraction mechanisms (Lexical n-grams, Structural AST trees, Semantic UniXcoder embeddings, Behavioral sandboxed execution, and AI heuristic signals) feeding into raw evidence arrays prior to adaptive fusion.

---

# Figure 4: Adaptive Evidence Fusion and Instructor Feedback Loop

### Suitability
- **Primary Use**: Research Paper Contribution Section, Conference Presentation Slide
- **Target Audience**: Machine Learning Researchers, Academic Integrity Officers

```mermaid
flowchart TD
    subgraph FusionPipeline["Adaptive Evidence Fusion"]
        LexEv["Lexical Evidence"] --> EvVec
        StructEv["Structural Evidence"] --> EvVec
        SemEv["Semantic Evidence"] --> EvVec
        BehEv["Behavioral Evidence"] --> EvVec
        AIEv["AI Generation Signal"] --> EvVec

        EvVec[Multi-View Evidence Vector X] --> LogReg[Adaptive Fusion Model<br/><i>L2-Penalized Logistic Regression</i>]
        LogReg --> FusedScore[Fused Similarity Score]
        FusedScore --> TransDetect[Transformation Detection]
        TransDetect --> Explanation[Explainable Verdict & Narrative]
    end

    subgraph FeedbackLoop["Instructor Feedback Loop"]
        Instructor([Instructor Review]) --> Verdict{Review Verdict}
        Verdict -- Confirmed --> ConfirmedFb[Confirmed Plagiarism Label = 1]
        Verdict -- False Positive --> FalsePosFb[False Positive Label = 0]

        ConfirmedFb --> FeedbackDB[(Feedback Database)]
        FalsePosFb --> FeedbackDB

        FeedbackDB --> AdaptiveTrainer[Adaptive Trainer Module]
        AdaptiveTrainer --> Retrain[Refit Model & Normalize Positive Weights]
        Retrain -. "Update Active Weights" .-> LogReg
    end
```

### Explanation & Components Represented
Demonstrates EHSA's core research innovation: how multi-channel evidence vectors feed into an L2-penalized Logistic Regression model to compute fused scores, and how instructor verdicts (`confirmed` vs `false_positive`) enter a closed feedback loop to retrain and update active feature weights over time.

---

# Figure 5: EHSA Research Evaluation Pipeline

### Suitability
- **Primary Use**: Research Paper Experiments Section, Thesis Evaluation Chapter
- **Target Audience**: Empirical Software Engineering Researchers, Benchmark Evaluators

```mermaid
flowchart TD
    subgraph DataPrep["Research Benchmark Construction"]
        SourceProgs[30 Source Program Families P001-P030] --> ControlTrans[Controlled Transformations]
        ControlTrans --> GroundTruth[Ground-Truth Verification]
        GroundTruth --> BenchmarkDS[150-Pair Evaluation Dataset<br/><i>120 Positive / 30 Negative</i>]
    end

    subgraph EvaluationProtocol["5-Fold Grouped Stratified Cross-Validation"]
        BenchmarkDS --> GroupSplit[Grouped Split by Source Program ID]
        GroupSplit --> Fold1[Fold 1: P001-P006]
        GroupSplit --> Fold2[Fold 2: P007-P012]
        GroupSplit --> Fold3[Fold 3: P013-P018]
        GroupSplit --> Fold4[Fold 4: P019-P024]
        GroupSplit --> Fold5[Fold 5: P025-P030]
    end

    subgraph EngineEval["Model Benchmarking"]
        Fold1 & Fold2 & Fold3 & Fold4 & Fold5 --> Engine[EHSA Analysis Engine]
        Engine --> SingleChannels[Single Channels<br/><i>Lexical / Structural / Semantic / Behavioral</i>]
        Engine --> FixedFuse[Fixed Fusion<br/><i>Equal Weights</i>]
        Engine --> AdaptFuse[Adaptive Fusion<br/><i>Logistic Regression</i>]
    end

    subgraph MetricsOutput["Evaluation Metrics & Ablation Results"]
        SingleChannels & FixedFuse & AdaptFuse --> Metrics[Compute Metrics]
        Metrics --> P[Precision: 0.983]
        Metrics --> R[Recall: 0.975]
        Metrics --> F1[F1-Score: 0.979]
        Metrics --> AUC[AUC-ROC: 0.996]
    end
```

### Explanation & Components Represented
Visually isolates the offline experimental benchmarking pipeline. Displays dataset construction across 30 Computer Science program families, 5-Fold Grouped Stratified Cross-Validation (guaranteeing zero data leakage across folds), strategy comparison (single channel vs fixed fusion vs adaptive fusion), and benchmark performance outputs.

---

# Figure 6: EHSA Database Entity Relationship Diagram

### Suitability
- **Primary Use**: Thesis Database Chapter, Technical Documentation, System Manual
- **Target Audience**: Database Administrators, Backend Engineers

```mermaid
erDiagram
    USER ||--o{ RUN : "initiates / owns"
    USER ||--o{ FEEDBACK : "submits"
    RUN ||--o{ EVIDENCE : "contains (1-to-N cascade)"
    RUN ||--o{ FEEDBACK : "receives (1-to-N cascade)"

    USER {
        string id PK
        string username UK
        string email UK
        string password_hash
        string role "student|instructor|admin"
        int is_active
        datetime created_at
    }

    RUN {
        string id PK
        string user_id FK "nullable"
        string file_a_name
        string file_b_name
        float lexical_score
        float structural_score
        float semantic_score
        float behavioral_score
        float fusion_score
        string fusion_weights_used
        string transformation_type
        float transformation_confidence
        float ai_generation_likelihood
        datetime created_at
    }

    EVIDENCE {
        int id PK
        string run_id FK
        string dimension
        string file_ref
        int line_start
        int line_end
        string detail "JSON"
    }

    FEEDBACK {
        int id PK
        string run_id FK
        string user_id FK
        string verdict "confirmed|false_positive"
        datetime created_at
    }

    FUSION_WEIGHT_HISTORY {
        int id PK
        string weights "JSON"
        int trained_on_n_samples
        datetime created_at
    }
```

### Explanation & Components Represented
Presents the relational database schema implemented in SQLite (`ehsa.db`) via SQLAlchemy 2.0. Highlights the five core entities (`USER`, `RUN`, `EVIDENCE`, `FEEDBACK`, `FUSION_WEIGHT_HISTORY`), primary keys, foreign key constraints, and cascade relationships.

---

# Figure 7: EHSA Authentication and Authorization Flow

### Suitability
- **Primary Use**: Security Audit Report, Technical Documentation, Thesis Security Section
- **Target Audience**: Security Auditors, Compliance Officers, Backend Developers

```mermaid
flowchart TD
    Req[Incoming HTTP Request] --> HeaderCheck{Authorization Header Present?}
    HeaderCheck -- No --> GuestMode[Assign Guest Context<br/><i>user_id = None</i>]
    HeaderCheck -- Yes --> TokenCheck{Valid Bearer JWT Token?}
    
    TokenCheck -- Invalid / Expired --> Auth401[401 Unauthorized Response]
    TokenCheck -- Valid --> FetchUser[Query User Account from DB]
    
    FetchUser --> ActiveCheck{Is Account Active?}
    ActiveCheck -- Inactive --> Forbidden403[403 Account Deactivated Response]
    ActiveCheck -- Active --> UserResolved[User Context Resolved]
    
    UserResolved --> RoleGuard{Endpoint Requires Specific Role?}
    RoleGuard -- Role Denied --> Role403[403 Forbidden: Insufficient Role Privileges]
    RoleGuard -- Role Allowed --> ResourceGuard{Accessing Owned Run / Resource?}
    
    ResourceGuard -- IDOR Violation --> IDOR403[403 Forbidden: Access Denied to Resource]
    ResourceGuard -- Authorized --> ExecuteEndpoint[Execute API Endpoint Handler]
    GuestMode --> ExecuteEndpoint
```

### Explanation & Components Represented
Detail-oriented security decision flowchart tracing request authentication, JWT token signature validation, account status checks, Role-Based Access Control (RBAC) enforcement (`student`, `instructor`, `admin`), and Insecure Direct Object Reference (IDOR) resource ownership verification.

---

# Figure 8: EHSA Research-Paper Primary Architecture

### Suitability
- **Primary Use**: **IEEE / ACM Research Paper Figure 1**, Journal Paper Architecture Overview
- **Target Audience**: Paper Readers, Peer Reviewers, Conference Attendees

```mermaid
flowchart TD
    Input[Source Code Pair] --> Prep[Preprocessing]
    
    subgraph MultiView["Multi-View Similarity Engine"]
        Prep --> Lexical[Lexical Channel]
        Prep --> Structural[Structural Channel]
        Prep --> Semantic[Semantic Channel]
        Prep --> Behavioral[Behavioral Channel]
    end

    Lexical --> Evidence[Multi-View Evidence Vector]
    Structural --> Evidence
    Semantic --> Evidence
    Behavioral --> Evidence

    Evidence --> Fusion[Adaptive Weight Fusion]
    Fusion --> Detection[Transformation Detection]
    Detection --> Explanation[Evidence-Grounded Explanation]
    Explanation --> Human[Human Investigation & Verdict]

    Human -. "Instructor Verdict (Confirmed / False Positive)" .-> Feedback[Feedback Database]
    Feedback -. "Retrain Weights" .-> Fusion
```

### Explanation & Components Represented
The primary publication figure for academic papers. Formatted specifically for IEEE/ACM single-column or double-column layouts, clearly summarizing EHSA's core paradigm: **Source-code pair $\rightarrow$ Multi-view analysis $\rightarrow$ Traceable evidence $\rightarrow$ Adaptive fusion $\rightarrow$ Transformation detection $\rightarrow$ Grounded explanation $\rightarrow$ Human investigation $\rightarrow$ Closed-loop feedback**.

---

# Figure 9: Presentation Version (Slide-Optimized Overview)

### Suitability
- **Primary Use**: **IFGSCET-2026 Presentation Slides**, Demo Opening Slide
- **Target Audience**: Conference Audience, Slide Viewer

```mermaid
flowchart LR
    P[PROBLEM<br/><i>Plagiarism & AI Rewrites</i>] --> M[MULTI-VIEW ANALYSIS<br/><i>Lexical + Structural + Semantic + Behavioral</i>]
    M --> E[EVIDENCE<br/><i>Traceable Line & AST Logs</i>]
    E --> A[ADAPTIVE FUSION<br/><i>Learned Feedback Weights</i>]
    A --> X[EXPLANATION<br/><i>Verdicts & Narratives</i>]
    X --> H[HUMAN INVESTIGATION<br/><i>Advisory Decision Support</i>]
```

### Explanation & Components Represented
Ultra-clean 6-block linear slide diagram designed for presentation decks. Instantly communicates the EHSA story in under 5 seconds.

---

# Figure 10: Technical Documentation Version (Implementation Topology)

### Suitability
- **Primary Use**: Developer Onboarding Guide, System Maintenance Manual
- **Target Audience**: Software Engineers, DevOps Engineers

```mermaid
flowchart TD
    NextJS[Next.js 16 Frontend] --> Axios[Axios API Client]
    Axios -- "HTTP / JSON" --> FastAPI[FastAPI Server]
    FastAPI --> APIRoutes[API Router Layer]
    APIRoutes --> Preprocess[Preprocessing Engine]
    Preprocess --> SimModules[Similarity Modules]
    SimModules --> FusionEngine[Fusion Engine]
    FusionEngine --> ExplGenerator[Explanation Generator]
    ExplGenerator --> SQLAlchemy[SQLAlchemy 2.0 Async ORM]
    SQLAlchemy --> SQLite[(SQLite ehsa.db)]
```

### Explanation & Components Represented
Concise software component stack mapping the call hierarchy from Next.js UI down to SQLite database storage.

---

# Summary of Figure Suitability & Usage Matrix

| Figure | Diagram Title | Research Paper | Presentation | Thesis | Technical Docs |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Figure 1** | EHSA High-Level System Architecture | | | ⭐ | ⭐ |
| **Figure 2** | EHSA End-to-End Similarity Analysis Workflow | | | ⭐ | ⭐ |
| **Figure 3** | EHSA Multi-View Similarity Analysis Pipeline | ⭐ | ⭐ | ⭐ | |
| **Figure 4** | Adaptive Evidence Fusion & Instructor Feedback Loop | ⭐ | ⭐ | ⭐ | |
| **Figure 5** | EHSA Research Evaluation Pipeline | ⭐ | | ⭐ | |
| **Figure 6** | EHSA Database Entity Relationship Diagram | | | ⭐ | ⭐ |
| **Figure 7** | EHSA Authentication and Authorization Flow | | | ⭐ | ⭐ |
| **Figure 8** | **EHSA Research-Paper Primary Architecture** | **⭐ PRIMARY** | ⭐ | ⭐ | |
| **Figure 9** | Presentation Version (Slide-Optimized) | | **⭐ PRIMARY** | | |
| **Figure 10**| Technical Documentation Version | | | | **⭐ PRIMARY** |

