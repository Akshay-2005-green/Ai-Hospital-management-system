"""Custom Flask CLI commands."""
import click

from app.extensions import db


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create all tables (prototype use only; prefer `flask db upgrade`)."""
        db.create_all()
        click.echo("Tables created.")

    @app.cli.command("seed-db")
    def seed_db():
        """Insert a small, connected sample dataset for local development."""
        from app.seed import seed_sample_data

        seed_sample_data()
        click.echo("Sample data inserted.")
