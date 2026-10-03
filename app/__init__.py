"""Application factory for the AI-Powered Hospital Flow Management System."""
import os

from flask import Flask, jsonify

from app.config import CONFIG_MAP
from app.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(config_name, CONFIG_MAP["development"]))

    db.init_app(app)

    # Importing the models package registers every table on db.metadata,
    # which Flask-Migrate / Alembic needs for autogeneration.
    from app import models  # noqa: F401

    migrate.init_app(app, db)

    from app.cli import register_cli

    register_cli(app)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app
