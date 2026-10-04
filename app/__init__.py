from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app(config_name=None):

    flask_app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    flask_app.config.from_object(Config)

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

    # Import routes
    from app.routes import (
        auth_bp,
        patient_bp,
        hospitals_bp,
        appointments_bp,
        queue_bp,
        notifications_bp,
    )

    # Register blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(patient_bp)
    flask_app.register_blueprint(hospitals_bp)
    flask_app.register_blueprint(appointments_bp)
    flask_app.register_blueprint(queue_bp)
    flask_app.register_blueprint(notifications_bp)

    return flask_app