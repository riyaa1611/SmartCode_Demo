# SmartCode — Career & Portfolio Positioning

## 🎯 Elevator Pitch

> **SmartCode is an AI code review engine that reads GitHub issues, analyzes PRs for security/performance/requirement alignment, and produces a 0-100% "merge confidence score" — answering if a PR is safe to ship, not just if it compiles.**

---

## 📄 Resume Description

**SmartCode — AI-Powered Code Review Engine** *(Personal Project / Open Source)*

- Architected an **event-driven AI code review pipeline** using FastAPI, Celery, Redis, and PostgreSQL that processes GitHub PRs via webhooks, runs multi-dimensional LLM analysis (security, performance, requirement drift), and auto-posts structured findings as PR comments
- Designed a **PR Approval Confidence Score** (0-100) combining 5 weighted dimensions — requirement alignment (30%), security safety (25%), code quality (20%), test coverage signal (15%), and static analysis (10%) — with automated APPROVE / REVIEW_NEEDED / CHANGES_REQUESTED verdicts
- Built production-grade **LLM prompt engineering** with structured JSON output schemas, anti-hallucination guardrails, diff truncation for context window management, and confidence scoring per finding
- Implemented **quantified code health metrics**: Bug Risk Score, Security Severity Index, and Technical Debt Indicator using AST-based cyclomatic complexity analysis and severity-weighted aggregation

---

## 🖥️ Portfolio Explanation

SmartCode solves a real problem in software teams: code reviews are slow, inconsistent, and miss whether the PR actually implements what the issue asked for.

I built an end-to-end AI system that acts as a "Senior Staff Engineer" reviewer. When a developer opens a PR on GitHub, SmartCode automatically:

1. **Extracts context** — the PR diff, linked issue requirements, and project documentation
2. **Runs static analysis** — AST-based complexity scoring and diff structure analysis
3. **Reasons with an LLM** — using production-grade prompts that enforce structured JSON output, reference only changed code, and include anti-hallucination rules
4. **Calculates a confidence score** — a composite 0-100 rating across 5 dimensions (requirements, security, quality, tests, static analysis) with automated merge verdicts
5. **Posts a GitHub comment** — formatted with severity levels, code snippets, suggested fixes, and CWE/OWASP references

The system processes everything asynchronously via Celery workers backed by Redis, stores findings in PostgreSQL, and serves a React dashboard for historical analysis.

What makes it different from tools like CodeQL or SonarQube: those check syntax rules. SmartCode checks *intent* — whether the code does what was asked.

---

## 🎤 Interview Talking Points

### 1. AI Engineering / LLM Integration
- **Prompt engineering at production scale**: Designed 4 specialized prompt templates with strict JSON schemas, system-level persona instructions, and anti-hallucination rules ("If the code is fine, say so. Never invent problems.")
- **Structured output enforcement**: Used `response_format: json_object` with fallback markdown-fence stripping for models that wrap responses
- **Context window management**: Implemented diff truncation (first/last halves with truncation marker) to handle large PRs within token limits
- **Multi-pass analysis**: Each PR runs through 4 independent LLM passes (requirements, security, performance, quality) with findings aggregated and de-duplicated
- **Confidence calibration**: Each LLM finding includes a model-assigned confidence score (0.0-1.0) that feeds into the composite scoring algorithm

### 2. Backend Systems Design
- **Event-driven architecture**: GitHub webhook → signature verification → database record → Celery task queue → async analysis → result storage → GitHub API callback
- **Async task processing**: Celery workers with Redis broker for non-blocking PR analysis (reviews can take 30-60 seconds with LLM calls)
- **Database design**: SQLAlchemy models with dialect-aware column types (PostgreSQL JSONB/ARRAY for production, generic JSON for SQLite dev)
- **Graceful degradation**: Worker module falls back to no-op if Celery/Redis unavailable; app still serves API endpoints for frontend development
- **Configuration management**: Environment-based settings with sensible defaults for local development (SQLite, dummy keys)

### 3. Developer Tooling / GitHub Integration
- **GitHub App authentication**: App-level auth with installation tokens for repository access
- **Webhook processing**: SHA-256 signature verification, event type routing (pull_request, issue_comment)
- **PR comment management**: Idempotent commenting — SmartCode updates its existing comment instead of posting duplicates
- **Issue-PR linking**: Regex-based extraction of "fixes #123" / "closes #456" references to connect PRs to requirements

### 4. System Design / Architecture
- **Multi-stage pipeline**: PR → Context Extraction → Static Analysis → AI Reasoning → Scoring → Storage → Feedback — each stage is independently testable
- **Composite scoring algorithm**: Weighted multi-dimensional scoring (5 axes × individual weights) with threshold-based verdict classification
- **Metrics framework**: Four quantified indicators (Bug Risk, Security Index, Tech Debt, Confidence) with clear formulas and rating scales
- **API design**: RESTful endpoints for reviews, metrics, and analysis triggers; demo endpoint for UI development without live data

### 5. Data Engineering
- **Diff parsing**: Custom parser that extracts structured file changes (added/modified/removed functions, dependency changes) from unified diff format
- **AST analysis**: Python `ast` module visitor pattern for cyclomatic complexity, nesting depth, and function count metrics
- **Requirement extraction**: Regex-based extraction of requirements (bullet lists), acceptance criteria (checkboxes), and edge cases from GitHub issue bodies
- **Findings aggregation**: Multi-source finding merging with backwards-compatible handling of legacy and new structured formats

---

## 🏷️ Keywords for ATS / LinkedIn

`AI Engineering` · `LLM` · `Prompt Engineering` · `FastAPI` · `Python` · `React` · `TypeScript` · `PostgreSQL` · `Redis` · `Celery` · `Docker` · `GitHub API` · `Webhooks` · `AST Analysis` · `Code Review` · `Developer Tools` · `System Design` · `Event-Driven Architecture` · `Microservices` · `CI/CD`
