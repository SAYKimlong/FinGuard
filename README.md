# FinGuard

> **Understand the risk before you sign.**

FinGuard is a multilingual AI Personal Finance Agent that helps consumers understand financial agreements, identify potentially concerning clauses, calculate borrowing costs, evaluate affordability, and explore financial stress scenarios — before committing to financial obligations.

Built for the **2026 Shenzhen International FinTechathon** — International Track, Topic A: Personal Finance Assistant.

---

## 🎯 What FinGuard Does

| Capability | Description |
|------------|-------------|
| **UNDERSTAND** | Extract and explain financial documents in plain language |
| **EVALUATE** | Identify concerning clauses and calculate financial exposure |
| **SIMULATE** | Evaluate how obligations affect your budget under stress scenarios |

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     │ + pgvector  │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │   Celery     │──── Redis
                    │   Workers    │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   Ollama     │
                    │  (LLM/Embed) │
                    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- Ollama with `llama3.1:8b` and `nomic-embed-text`
- Redis (WSL2 or native)

### 1. Clone and Configure

```bash
git clone https://github.com/SAYKimlong/FinGuard.git
cd FinGuard
cp .env.example .env
# Edit .env with your settings
```

### 2. Start PostgreSQL (Docker)

```bash
docker compose up -d postgres
```

### 3. Start Ollama

```bash
ollama serve
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 4. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# In another terminal — start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 6. Open the App

Navigate to [http://localhost:3000](http://localhost:3000)

---

## 📁 Project Structure

```
FinGuard/
├── frontend/                  # Next.js App Router
│   ├── src/
│   │   ├── app/              # Pages and routes
│   │   ├── components/       # Reusable UI components
│   │   ├── lib/              # Utilities, API client, types
│   │   └── ...
│   └── package.json
├── backend/                   # FastAPI + Python
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── models/           # SQLAlchemy models
│   │   ├── risk_engine/      # Deterministic calculations
│   │   ├── ai/               # LLM provider, tools, prompts
│   │   ├── ocr/              # Document text extraction
│   │   ├── rag/              # Retrieval-augmented generation
│   │   └── workers/          # Celery async tasks
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest test suite
│   └── requirements.txt
├── docs/                      # Competition documentation
├── test_data/                 # Synthetic test documents
├── docker-compose.yml         # PostgreSQL + pgvector
├── .env.example
└── README.md
```

## 🧪 Running Tests

```bash
cd backend
pytest -v
pytest tests/test_risk_engine.py -v      # Financial calculations
pytest tests/test_security.py -v          # Authorization tests
```

## 🔒 Security

- JWT authentication with bcrypt password hashing
- Per-user data isolation on all resources
- File type validation with magic byte checking
- Upload size limits
- CORS restrictions
- Rate limiting
- Parameterized database queries (SQLAlchemy ORM)
- Prompt injection defenses
- No plaintext password storage
- Audit event logging

See [docs/security_self_assessment.md](docs/security_self_assessment.md) for the full security report.

## 🌍 Language Support

| Language | Status | OCR | Clause Extraction | Explanation |
|----------|--------|-----|-------------------|-------------|
| English | ✅ Production | ✅ | ✅ | ✅ |
| Khmer | 🔶 Beta | 🔶 Testing | 🔶 Testing | ✅ English |
| Thai | 📋 Planned | — | — | — |
| Vietnamese | 📋 Planned | — | — | — |
| Others | 📋 Architecture Ready | — | — | — |

## ⚠️ Disclaimers

- FinGuard is a **consumer information tool**, not a legal or financial advisor.
- Findings are **analytical indicators**, not definitive legal judgments.
- Always consult qualified professionals for financial and legal decisions.
- Synthetic demo data is clearly labeled and should not be treated as real.
- Risk scores are calculated by deterministic formulas, not invented by AI.

## 📄 License

This project is built for the 2026 Shenzhen International FinTechathon competition.

---

*Built with ❤️ for financial transparency*
