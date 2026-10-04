from datetime import date
from app.extensions import db


class Patient(db.Model):
    __tablename__ = "patients"

    patient_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True, default="")

    phone = db.Column(db.String(20), nullable=True, unique=True, default="0000000000")
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    appointments = db.relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    medical_records = db.relationship(
        "MedicalRecord",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    queue_entries = db.relationship(
        "QueueEntry",
        back_populates="patient",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    ml_predictions = db.relationship(
        "MLPrediction",
        back_populates="patient",
    )
