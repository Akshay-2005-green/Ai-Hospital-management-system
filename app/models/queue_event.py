from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin, enum_check
from app.models.enums import QueueEventType


class QueueEvent(ReprMixin, CreatedAtMixin, db.Model):
    """Append-only flow history; the main source of ML training data."""

    __tablename__ = "queue_events"

    event_id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), index=True)
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.appointment_id"), index=True
    )
    queue_entry_id = db.Column(
        db.Integer, db.ForeignKey("queue_entries.queue_entry_id"), index=True
    )
    event_type = db.Column(db.String(30), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False, index=True)
    duration = db.Column(db.Float)  # minutes
    description = db.Column(db.Text)

    # Relationships
    hospital = db.relationship("Hospital", back_populates="queue_events")
    doctor = db.relationship("Doctor", back_populates="queue_events")
    appointment = db.relationship("Appointment", back_populates="queue_events")
    queue_entry = db.relationship("QueueEntry", back_populates="events")

    __table_args__ = (
        enum_check("event_type", QueueEventType, "ck_queue_events_event_type"),
        db.Index("ix_queue_events_hospital_time", "hospital_id", "event_time"),
        db.Index("ix_queue_events_doctor_time", "doctor_id", "event_time"),
    )
