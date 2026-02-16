
# Smart Code Review Bot

Lightweight service that analyzes pull requests and code to surface findings
(security, design, feature drift, performance). This repo contains the API
server (FastAPI), database models, worker hooks, and a small placeholder UI.

Quickstart (local, minimal)
---------------------------
- Create a Python virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
```

- Install core dependencies (project `requirements.txt` is used by Docker):

```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

- Create the database tables (the project uses SQLite by default, or Postgres
    when using Docker compose):

```bash
.venv\Scripts\python.exe init_db.py
```

- Run the app locally with Uvicorn:

```bash
.venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8084 --reload
```

Docker Compose (Postgres + Redis + app)
--------------------------------------
This repo includes a `docker-compose.yml` that brings up Postgres and Redis
and runs the app in a container. To use it:

```bash
docker compose up --build -d
```

The compose file sets these environment variables for the app service:
- `DATABASE_URL=postgresql://user:password@smartcode-db:5432/smart_review`
- `REDIS_URL=redis://smartcode-redis:6379/0`

After compose starts, create the schema inside the container (or run from
host if your `DATABASE_URL` points to the containerized Postgres):

```bash
docker compose exec smartcode-app python init_db.py
```

Seeding sample data
--------------------
I added `seed_db.py` to insert a sample `Review` and two `Finding` rows for
quick testing. Run it locally with the venv or inside the app container:

```bash
.venv\Scripts\python.exe seed_db.py
# or
docker compose exec smartcode-app python seed_db.py
```

Available endpoints (examples)
------------------------------
- `GET /health` — basic health check
- `GET /demo/review/{pr_id}` — demo review response (UI preview)
- `GET /api/review/{id}` — fetch a review (DB-backed)

Serving the UI
--------------
There is a simple placeholder UI at `ui/index.html`. If you want this served
by the FastAPI app, I can add a static route so `http://localhost:8084/` will
return it.

Building and serving the React frontend (production)
-----------------------------------------------
If you use the React frontend in `frontend/`, build it and serve the `dist`
output from the FastAPI app. Example workflow:

```bash
# from repo root
cd frontend
npm install
npm run build
# built files will appear in `frontend/dist`
```

After building, the FastAPI app will automatically serve the `frontend/dist`
files at the root path (if present). See `main.py` for the mount logic.

Frontend development (proxy to backend)
--------------------------------------
For development, the Vite dev server proxies API requests to the backend
(`http://localhost:8084`). You can copy `frontend/.env.example` to
`frontend/.env` and edit `VITE_API_URL` or leave it empty to use the proxy.


Development notes
-----------------
- `config.py` contains lightweight settings. Defaults are set to point to the
    Docker Postgres/Redis on `localhost` when using compose, and to SQLite for
    quick local runs.
- `models.py` detects the DB dialect and uses appropriate column types for
    Postgres (ARRAY/JSONB) or generic JSON for SQLite.
- `worker.py` includes a Celery fallback so the app can run even without a
    running Celery worker during quick local development.

Common commands
---------------
- Build & run compose: `docker compose up --build -d`
- View logs: `docker compose logs -f smartcode-app`
- Run DB init inside container: `docker compose exec smartcode-app python init_db.py`

Contributing
------------
If you'd like, I can:
- Serve the `ui/index.html` from the app and wire basic UI calls to the API.
- Add example frontend code (React/Vanilla) and a small script to seed more
    realistic review data.

License
-------
MIT-style (no license file included). Ask if you want a specific license.

Contact / next steps
--------------------
Tell me if you want the UI served from the app, more seed data, or a basic
React/Vanilla implementation — I can add it next.


## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   GitHub App    │───▶│  Webhook Handler │───▶│  Data Pipeline   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                              │                         │
                              ▼                         ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │  API Endpoints   │    │  Analysis Engine │
                    └──────────────────┘    └──────────────────┘
                              │                         │
                              ▼                         ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │   PostgreSQL     │    │  LLM Reviewer    │
                    └──────────────────┘    └──────────────────┘
```

## Components

### Phase 1: GitHub Integration & Data Pipeline
- GitHub App with webhook handlers for PR events
- Data collection from PRs, issues, and project documentation
- Structured data storage in PostgreSQL

### Phase 2: Intelligent Analysis Engine
- Requirement understanding from issues
- Code analysis using static analysis tools
- LLM-powered review for completeness, security, and performance

### Phase 3: GitHub Actions Integration
- GitHub Actions workflow template
- PR comment formatting with suggestions

### Phase 4: Dashboard & Metrics
- Web dashboard for repository insights
- Metrics tracking for review effectiveness

### Phase 5: Advanced Features
- Learning from developer feedback
- Custom rule engine
- Dependency risk analysis
- Test coverage validation
- Documentation drift detection

## Setup

1. Create a GitHub App with appropriate permissions
2. Configure webhook URL to point to your deployment
3. Set environment variables in `.env` file
4. Run with Docker: `docker-compose up`

## API Endpoints

- `POST /webhook/github` - Receives GitHub webhooks
- `GET /api/review/{pr_id}` - Retrieves review status
- `POST /api/analyze` - Manually triggers analysis for a PR
- `GET /api/metrics/{repo}` - Shows review stats for repository

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Celery
- **Database**: PostgreSQL 15+
- **LLM**: OpenRouter (DeepSeek R1)
- **GitHub**: PyGithub library
- **Static Analysis**: tree-sitter, semgrep
- **Frontend**: React 18+, Recharts
- **Deployment**: Docker, Docker Compose