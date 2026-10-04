from datetime import datetime
from app.extensions import db
from app.models.enums import QueueStatus


class QueueEntry(db.Model):
    __tablename__ = "queue_entries"

    queue_entry_id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.appointment_id"),
        nullable=False,
        unique=True,
        index=True,
    )
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )
    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=False,
        index=True,
    )

    department = db.Column(db.String(100), nullable=False, index=True)
    queue_number = db.Column(db.String(20), nullable=False)
    room = db.Column(db.String(50), nullable=True, default="Room 101")
    position = db.Column(db.Integer, nullable=False, default=1)

    status = db.Column(
        db.String(40),
        nullable=False,
        default=QueueStatus.WAITING.value,
        index=True,
    )

    joined_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    called_at = db.Column(db.DateTime, nullable=True)
    consultation_started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    appointment = db.relationship(
        "Appointment",
        back_populates="queue_entry",
    )
    patient = db.relationship(
        "Patient",
        back_populates="queue_entries",
    )
    hospital = db.relationship("Hospital")
