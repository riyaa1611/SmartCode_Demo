import os
from typing import Optional


class Settings:
    """Lightweight settings loader for quick local runs.

    Uses environment variables and falls back to sensible defaults for
    local testing (SQLite DB, dummy keys).
    """
    # GitHub App settings
    github_app_id: str = os.getenv("GITHUB_APP_ID", "local_test_app_id")
    github_private_key: str = os.getenv("GITHUB_PRIVATE_KEY", "")
    github_webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "local_test_webhook_secret")

    # Database settings
    # If `DATABASE_URL` is provided in the environment, use it (for compose
    # or production). If not set, fall back to a local SQLite DB for quick
    # developer runs so the app doesn't require Postgres to start.
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dev.db"
    )

    # Anthropic API settings
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Redis settings for Celery (Docker mapped port)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # GitHub API settings
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")


settings = Settings()