from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from routes import webhook, api, health
from database import engine, Base
import models
import os

# Create database tables (best-effort). If the configured DB is not
# available (e.g., Postgres not running in dev), log a warning and
# continue so the app can still start for UI development.
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: could not create database tables at startup: {e}")

app = FastAPI(
    title="Smart Code Review Bot",
    description="AI-powered code review tool tha\\\\t validates PRs against actual requirements",
    version="1.0.0"
)

# CORS configuration - allow frontend to communicate with backend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/webhook")
app.include_router(api.router, prefix="/api")
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Smart Code Review Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-code-review-bot"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.svg")

# Serve built frontend (if present) — mounted after API routes so API endpoints
# are matched first. This prevents static files from shadowing `/health` etc.
dist_path = Path(__file__).parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")

if __name__ == "__main__":
    try:
        import uvicorn
        # Using port 8084 as per project configuration
        uvicorn.run(app, host="0.0.0.0", port=8084)
    except ImportError:
        print("Error: uvicorn not installed. Please run 'pip install -r requirements.txt'")
        exit(1)