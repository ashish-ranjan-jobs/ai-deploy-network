# 🚀 AI Deploy Network — Builder Profile Platform

[![CI/CD Pipeline](https://github.com/ashish-ranjan-jobs/ai-deploy-network/actions/workflows/ci.yml/badge.svg)](https://github.com/ashish-ranjan-jobs/ai-deploy-network/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **"Connecting organisations with professionals who can demonstrate what they've actually built, deployed, and achieved."**  
> *Founded by James Blewman, Founder & CEO of AI Deploy Network.*

---

## 🌟 Overview

**AI Deploy Network** is the global directory of verified AI implementation expertise. Instead of relying solely on resumes or speculative claims, the platform allows AI practitioners to:
1. **Showcase Real-World AI Deployments**: Publish documented case studies with architectural details, models, libraries, and frameworks used.
2. **Demonstrate Measurable ROI**: Highlight quantified impact (e.g., latency reductions, hours saved, accuracy benchmarks, revenue growth).
3. **Earn Founding Builder Recognition**: The first 500 qualifying builders receive permanent **Founding Builder status** with a unique membership number (`#001` to `#500`).
4. **Export Certified Case Studies & Portfolios**: Download branded, publication-ready PDFs to share with prospective employers and clients.
5. **Enable Discovery**: Organisations and recruiters can search proven implementations by AI stack (RAG, LLMs, Computer Vision), industry, and keywords.

---

## 🛠️ Architecture & Tech Stack

```
ai-deploy-network/
├── src/
│   ├── main.py                  # FastAPI application entrypoint & lifespan
│   ├── config.py                # Pydantic BaseSettings environment manager
│   ├── database.py              # SQLAlchemy engine & session factory
│   ├── models/                  # SQLAlchemy ORM models (User, Membership, Deployment, Verification)
│   ├── schemas/                 # Pydantic v2 validation schemas
│   ├── services/                # Business logic & domain services
│   │   ├── auth_service.py      # Direct bcrypt hashing & JWT tokens
│   │   ├── builder_service.py   # Builder management & directory
│   │   ├── deployment_service.py# AI Case study CRUD, search & verification
│   │   ├── membership_service.py# Founding Builder 500-slot counter & assignments
│   │   └── pdf_service.py       # High-fidelity PDF generator via ReportLab
│   ├── routers/                 # Modular API & Web handlers
│   │   ├── auth.py              # REST: /api/auth
│   │   ├── builders.py          # REST: /api/builders
│   │   ├── deployments.py       # REST: /api/deployments
│   │   ├── search.py            # REST: /api/search
│   │   ├── admin.py             # REST: /api/admin
│   │   └── web.py               # HTML: Jinja2 UI web routes
│   ├── templates/               # Responsive Jinja2 templates (Tailwind CSS)
│   └── static/                  # CSS styling, badges & client JS
├── tests/                       # Pytest test suite (19 unit/integration tests)
├── .github/workflows/ci.yml     # Automated lint and test workflow
├── Dockerfile                   # Multi-stage production container
└── docker-compose.yml           # Compose specification
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.12+
- Git

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/ashish-ranjan-jobs/ai-deploy-network.git
cd ai-deploy-network

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

### 4. Run Development Server
```bash
uvicorn src.main:app --reload --port 8000
```
Open your browser and navigate to:
- **Web Platform:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing & Code Quality

Run tests and linter verification:
```bash
source venv/bin/activate

# Run pytest suite
pytest -v

# Run Ruff linter and code formatter
ruff check .
ruff format --check .
```

---

## 🐳 Docker Deployment

Run with Docker Compose:
```bash
docker compose up -d --build
```

Health check:
```bash
curl http://localhost:8000/api/health
```

---

## 📄 License

MIT License. Designed and engineered for the AI Deploy Network Builder Program.
