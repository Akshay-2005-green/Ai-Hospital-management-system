from flask import Flask
from sqlalchemy import text

from app.config import Config
from app.extensions import db, migrate


def ensure_queue_schema():
    inspector = db.inspect(db.engine)
    if inspector.has_table("doctors"):
        doctor_columns = {
            column["name"]
            for column in inspector.get_columns("doctors")
        }
        if "status" not in doctor_columns:
            with db.engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE doctors "
                        "ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE'"
                    )
                )

    if inspector.has_table("queue_entries"):
        columns = {column["name"] for column in inspector.get_columns("queue_entries")}
        with db.engine.begin() as connection:
            if "doctor_id" not in columns:
                connection.execute(text("ALTER TABLE queue_entries ADD COLUMN doctor_id INTEGER"))
                connection.execute(text("UPDATE queue_entries SET doctor_id = 1 WHERE doctor_id IS NULL"))
            if "is_emergency" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE queue_entries "
                        "ADD COLUMN is_emergency BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )


def create_app(config_name=None):

    flask_app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    flask_app.config.from_object(Config)

    if config_name == "testing":
        flask_app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite://",
            WTF_CSRF_ENABLED=False,
        )

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Import all models
    from app.models import (
        Patient,
        Hospital,
        Bed,
        Doctor,
        Appointment,
        QueueEntry,
        QueueEvent,
        DoctorAvailability,
        MedicalRecord,
        Notification,
        MLPrediction,
    )

    # Create database tables
    with flask_app.app_context():
        db.create_all()
        ensure_queue_schema()

    # Import routes
    from app.routes import (
        auth_bp,
        patient_bp,
        hospitals_bp,
        appointments_bp,
        queue_bp,
        notifications_bp,
        doctor_bp,
        receptionist_bp,
        symptoms_bp,
    )

    # Register blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(patient_bp)
    flask_app.register_blueprint(hospitals_bp)
    flask_app.register_blueprint(appointments_bp)
    flask_app.register_blueprint(queue_bp)
    flask_app.register_blueprint(notifications_bp)
    flask_app.register_blueprint(doctor_bp)
    flask_app.register_blueprint(receptionist_bp)
    flask_app.register_blueprint(symptoms_bp)

    return flask_app


app = create_app()