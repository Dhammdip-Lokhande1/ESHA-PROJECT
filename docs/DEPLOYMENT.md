# EHSA Deployment Guide

This guide provides instructions for deploying the Explainable Hybrid Similarity Analyzer (EHSA) using 100% free-tier services, as well as running the complete system locally via Docker Compose.

---

## 1. Zero-Cost Infrastructure Architecture

| Component | Service | Free Tier Capabilities | Environment Variables |
|---|---|---|---|
| **Frontend** | **Vercel** | Unlimited deployments, global CDN | `NEXT_PUBLIC_API_BASE_URL` |
| **Backend** | **Render** | 512 MB RAM, 0.1 CPU, automatic SSL | `DATABASE_URL`, `CORS_ORIGINS`, `MODEL_NAME` |
| **Database** | **Supabase** | 500 MB PostgreSQL database | `DATABASE_URL` |

---

## 2. Docker Compose (Local Deployment)

To run the entire system locally in isolated containers:

```bash
# Clone repository and navigate to root
cd "EHSA — Explainable Hybrid Similarity Analyzer"

# Build and start services
docker-compose up --build -d
```

Access points:
- **Frontend UI:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`

---

## 3. Production Deployment Step-by-Step

### 3.1 Database Setup (Supabase)
1. Create a free account on [Supabase](https://supabase.com/).
2. Create a new project named `ehsa-db`.
3. In Project Settings -> Database, copy the Connection String (URI).
4. Format the URL for async SQLAlchemy:
   ```text
   postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

### 3.2 Backend Deployment (Render)
1. Create a free account on [Render](https://render.com/).
2. Create a new **Web Service** and connect your GitHub repository.
3. Configure the build settings:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `DATABASE_URL`: `postgresql+asyncpg://...` (from Supabase)
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app`
   - `MODEL_NAME`: `microsoft/unixcoder-base`
5. Deploy Web Service. (Tables are auto-created on application lifespan startup).

### 3.3 Frontend Deployment (Vercel)
1. Create a free account on [Vercel](https://vercel.com/).
2. Import the Git repository into Vercel.
3. Configure project settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** `Next.js`
4. Set Environment Variables:
   - `NEXT_PUBLIC_API_BASE_URL`: `https://your-backend-on-render.onrender.com`
5. Deploy.

---

## 4. Security & Sandbox Disclosures

### 4.1 Behavioral Sandbox Execution
- EHSA executes Python code in a sandboxed `subprocess` with a 2.0-second timeout.
- On Linux deployment environments (e.g. Render containers), CPU time and RAM limits are enforced using `resource.setrlimit`.
- **Known Limitation:** On free-tier cloud hosting without dedicated root container access, OS-level network namespace isolation (`unshare -n`) cannot be guaranteed. Submitted code should be treated as untrusted, and deployments in high-security settings should run within dedicated Linux containers or gVisor sandboxes.

### 4.2 File Validation & Size Enforcement
- Request payloads are capped at **1 MB** server-side (`MAX_FILE_SIZE_BYTES`).
- Multi-file batch processing restricts file counts to 20 files per batch.
- Submissions undergo strict tokenization and AST parsing validation before execution.
