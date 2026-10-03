"""Environment-based configuration."""
import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///hospital_flow.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Business rule: how many upcoming patients are "prepared" in the queue.
    # Intentionally configuration, not a database constraint.
    TOP_N_PREPARATION_WINDOW = int(os.getenv("TOP_N_PREPARATION_WINDOW", 5))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
