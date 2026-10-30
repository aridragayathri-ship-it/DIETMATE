"""Application configuration for DietMate."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("DIETMATE_SECRET_KEY", "development-key-change-before-deployment")
    _database_url = os.environ.get("DATABASE_URL")
    if _database_url and _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)

    # SQLite under /tmp prevents Vercel's read-only filesystem crash, but
    # it is temporary and is NOT suitable for persistent production data.
    _default_sqlite_path = (
        Path("/tmp/dietmate.db") if os.environ.get("VERCEL")
        else BASE_DIR / "instance" / "dietmate.db"
    )
    SQLALCHEMY_DATABASE_URI = _database_url or f"sqlite:///{_default_sqlite_path.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
