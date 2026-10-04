import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "healthforge-development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + str(BASE_DIR / "hospital_flow.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB