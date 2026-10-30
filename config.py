"""Application configuration for DietMate."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("DIETMATE_SECRET_KEY", "development-key-change-before-deployment")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'instance' / 'dietmate.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
