<div align="center">
  <h1>🧠 SmartCode</h1>
  <p><strong>AI-powered code review that understands intent, not just syntax.</strong></p>
  <p>
    <a href="#demo-workflow">Demo</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#example-ai-review">Example Review</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#roadmap">Roadmap</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black" alt="React">
    <img src="https://img.shields.io/badge/LLM-DeepSeek_R1-FF6F00?logo=openai&logoColor=white" alt="LLM">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

---

## 🚨 The Problem

> **Code reviews are the biggest bottleneck in software delivery.**

- The average PR waits **24+ hours** for human review
- Reviews are **inconsistent** — quality depends entirely on who reviews
- Existing tools catch syntax issues but **miss the real question**:

  > *"Does this PR actually implement what was requested, and is it safe to merge?"*

| Tool | What It Does | What It Misses |
|------|-------------|---------------|
| GitHub Copilot | Autocompletes code | Doesn't review PRs or validate requirements |
| CodeQL / Semgrep | Rule-based SAST scanning | Can't reason about feature completeness |
| SonarQube | Tracks tech debt metrics | No PR-level intelligence, no requirement tracing |
| **SmartCode** | **AI review: requirement drift + security + performance + confidence scoring** | — |

---

## 💡 The Solution

**SmartCode** is an AI-powered GitHub App that reviews pull requests like a Senior Staff Engineer — checking not just *code quality*, but whether the code actually *does what the issue asked for*.

### ✨ Key Capability: PR Approval Confidence Score

A **0-100% composite score** that tells you *how safe it is to merge this PR*, combining:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Requirement Alignment | 30% | Do changes match linked issues? |
| Security Safety | 25% | Are there vulnerabilities? |
| Code Quality | 20% | Complexity, patterns, tech debt |
| Test Coverage Signal | 15% | Are tests added/modified? |
| Static Analysis | 10% | Linting + pattern results |

**Verdicts:**
- 🟢 **80-100**: `APPROVE` — safe to merge
- 🟡 **60-79**: `REVIEW_NEEDED` — human should check flagged items
- 🔴 **0-59**: `CHANGES_REQUESTED` — significant issues found

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SmartCode Platform                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐    │
│  │  GitHub App  │───▶│  Webhook Handler │───▶│   Celery Worker  │    │
│  │  (Webhooks)  │    │  (FastAPI)       │    │   (Redis Queue)  │    │
│  └─────────────┘    └──────────────────┘    └────────┬─────────┘    │
│                              │                        │              │
│                              ▼                        ▼              │
│                    ┌──────────────────┐    ┌──────────────────────┐  │
│                    │   REST API       │    │  Analysis Pipeline   │  │
│                    │  /api/review     │    │  ┌────────────────┐  │  │
│                    │  /api/metrics    │    │  │ Context Extract │  │  │
│                    │  /api/analyze    │    │  │ Static Analysis │  │  │
│                    └────────┬─────────┘    │  │ LLM Reasoning  │  │  │
│                             │              │  │ Confidence Score│  │  │
│                             ▼              │  └────────────────┘  │  │
│                    ┌──────────────────┐    └──────────┬───────────┘  │
│                    │   PostgreSQL     │               │              │
│                    │   (Reviews +     │◀──────────────┘              │
│                    │    Findings)     │                              │
│                    └──────────────────┘                              │
│                             │                                        │
│                             ▼                                        │
│                    ┌──────────────────┐    ┌──────────────────────┐  │
│                    │  React Dashboard │    │  GitHub PR Comment   │  │
│                    │  (Metrics + UI)  │    │  (Auto-posted)       │  │
│                    └──────────────────┘    └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Demo Workflow

```
Developer opens PR ──▶ GitHub fires webhook
                           │
                           ▼
                   POST /webhook/github
                   (signature verified)
                           │
                           ▼
                   Review record created
                   (status: "pending")
                           │
                           ▼
                   Celery task queued
                   analyze_pull_request()
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        Context Extraction        Static Analysis
        ├── PR diff               ├── AST complexity
        ├── Linked issues         ├── Diff structure
        └── Project docs          └── Dependency changes
              │                         │
              └────────────┬────────────┘
                           ▼
                    LLM AI Reasoning
                    ├── Requirement alignment
                    ├── Security scan
                    ├── Performance check
                    └── Code quality review
                           │
                           ▼
                   Confidence Scoring
                   ├── 5-dimension breakdown
                   ├── Risk flags
                   └── Verdict (APPROVE / REVIEW_NEEDED / CHANGES_REQUESTED)
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        Findings → DB              GitHub PR Comment
        (PostgreSQL)               (auto-posted)
```

---

## 📋 Example AI Review

When SmartCode reviews a PR, it automatically posts a comment like this:

```markdown
## 🤖 SmartCode AI Review

**PR Confidence Score: 72/100** — ⚠️ REVIEW NEEDED

### 📊 Score Breakdown
| Dimension | Score |
|-----------|-------|
| Requirement Alignment | 85/100 |
| Security Safety | 58/100 |
| Code Quality | 70/100 |
| Test Coverage | 45/100 |
| Static Analysis | 82/100 |

### 🔍 Findings (4 issues)

#### 🔴 CRITICAL — SQL Injection in payment query handler
**File:** `src/payments/queries.py:42`

query = f"SELECT * FROM payments WHERE user_id = '{user_id}'"

**Suggested Fix:** Use parameterized queries:
cursor.execute("SELECT * FROM payments WHERE user_id = %s", (user_id,))

**Confidence:** 95% · **Ref:** CWE-89, OWASP A03:2021

---

#### 🔴 HIGH — Missing pagination for transaction listing
**File:** `src/payments/routes.py:67`
Issue #189 requires paginated transaction listing.
Current implementation returns all records with no limit.

**Suggested Fix:** Add limit/offset parameters to the query.
**Confidence:** 88% · **Ref:** Issue #189

---

#### 🟡 MEDIUM — N+1 query in payment detail enrichment
**File:** `src/payments/service.py:91`
1001 queries instead of 2 for 1000 payments.

**Suggested Fix:** Prefetch merchants with a single IN query.
**Confidence:** 82%

---

#### 🟢 LOW — Missing error handling for external API call
**File:** `src/payments/gateway.py:128`

**Suggested Fix:** Add timeout and try/except for request failures.
**Confidence:** 76%

---

> 💡 Powered by SmartCode — AI Code Review that understands intent
```

---

## 📊 Metrics & Scoring

SmartCode calculates four measurable indicators for every review:

| Metric | Range | What It Measures |
|--------|-------|-----------------|
| **Bug Risk Score** | 0-100 | Inverse severity-weighted finding count |
| **Review Confidence** | 0-100% | Composite PR safety score |
| **Security Severity Index** | 0.0-10.0 | Vulnerability density per file |
| **Technical Debt Indicator** | 0.0-10.0 | Complexity + nesting + function sprawl |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, Celery |
| **Database** | PostgreSQL 15+ (SQLite for dev) |
| **Queue** | Redis 7+ |
| **LLM** | OpenRouter → DeepSeek R1 |
| **Static Analysis** | AST (Python), Tree-sitter, Semgrep |
| **GitHub** | GitHub App, Webhooks, PyGithub |
| **Frontend** | React 18+, TypeScript, Recharts, shadcn/ui |
| **Deployment** | Docker, Docker Compose |

---

## 🚀 Quick Start

### Local Development (minimal)

```bash
# 1. Clone and setup
git clone https://github.com/riyaa1611/SmartCode.git
cd SmartCode

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # PowerShell
# source .venv/bin/activate       # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY

# 5. Initialize database
python init_db.py

# 6. Run the server
uvicorn main:app --host 127.0.0.1 --port 8084 --reload
```

### Docker Compose (full stack)

```bash
docker compose up --build -d
docker compose exec smartcode-app python init_db.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Test the Demo Endpoint

```bash
curl http://localhost:8084/api/demo/review/1 | python -m json.tool
```

---

## 🗺️ Roadmap

- [x] GitHub App webhook integration
- [x] AI-powered PR review (security, performance, requirements)
- [x] PR Approval Confidence Score (0-100)
- [x] Structured findings with suggested fixes
- [x] Metrics dashboard (Bug Risk, Security Index, Tech Debt)
- [ ] Multi-repo evaluation framework
- [ ] Custom architectural rule definitions
- [ ] Learning from developer feedback (accept/dismiss signals)
- [ ] VS Code extension for inline review
- [ ] Dependency vulnerability scanning integration

---

## 📁 Project Structure

```
SmartCode/
├── main.py                          # FastAPI application entry point
├── config.py                        # Environment-based settings
├── models.py                        # SQLAlchemy models (Review, Finding)
├── worker.py                        # Celery worker — full analysis pipeline
├── database.py                      # Database engine + session
├── analysis_engine/
│   ├── llm_reviewer.py              # LLM-powered review (4 dimensions)
│   ├── prompt_templates.py          # Production-grade prompt templates
│   ├── confidence_scorer.py         # PR Approval Confidence Score
│   ├── metrics_calculator.py        # Bug Risk, Security Index, Tech Debt
│   ├── code_analyzer.py             # AST complexity + diff analysis
│   ├── requirement_extractor.py     # Issue → requirements parser
│   └── aggregator.py                # Findings aggregation + DB mapping
├── github_integration/
│   └── client.py                    # GitHub App auth + PR commenting
├── data_pipeline/
│   └── collector.py                 # PR, issue, and project data collector
├── routes/
│   ├── api.py                       # REST API endpoints
│   ├── webhook.py                   # GitHub webhook handler
│   └── health.py                    # Health check
├── frontend/                        # React 18 + TypeScript dashboard
├── docker-compose.yml               # Postgres + Redis + app
├── Dockerfile                       # Container build
└── CAREER.md                        # Resume + portfolio positioning
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p><strong>Built with ❤️ as a production-grade AI developer tool</strong></p>
  <p>
    <a href="#-the-problem">Problem</a> •
    <a href="#-the-solution">Solution</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-quick-start">Quick Start</a>
  </p>
</div>