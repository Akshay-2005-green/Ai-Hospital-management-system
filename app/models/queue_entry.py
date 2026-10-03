from app.extensions import db
from app.models.base import ReprMixin, enum_check, utcnow
from app.models.enums import QueueStatus


class QueueEntry(ReprMixin, db.Model):
    __tablename__ = "queue_entries"

    queue_entry_id = db.Column(db.Integer, primary_key=True)
    # unique=True enforces the MVP 1:1 rule. To keep historical queue states
    # later, drop the unique constraint and make Appointment.queue_entry a list.
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.appointment_id"), nullable=False, unique=True
    )
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False, index=True
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False, index=True
    )
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    queue_position = db.Column(db.Integer)
    status = db.Column(
        db.String(20), nullable=False, default=QueueStatus.WAITING.value, index=True
    )
    estimated_wait_time = db.Column(db.Float)  # minutes
    # Operational classification only; clinical priority stays with hospital rules.
    priority_type = db.Column(db.String(30), nullable=False, default="NORMAL")
    joined_at = db.Column(db.DateTime, default=utcnow)
    called_at = db.Column(db.DateTime)
    consultation_started_at = db.Column(db.DateTime)
    consultation_completed_at = db.Column(db.DateTime)

    # Relationships
    appointment = db.relationship("Appointment", back_populates="queue_entry")
    patient = db.relationship("Patient", back_populates="queue_entries")
    doctor = db.relationship("Doctor", back_populates="queue_entries")
    hospital = db.relationship("Hospital", back_populates="queue_entries")
    events = db.relationship("QueueEvent", back_populates="queue_entry")

    __table_args__ = (
        enum_check("status", QueueStatus, "ck_queue_entries_status"),
        db.Index("ix_queue_entries_doctor_status", "doctor_id", "status"),
        db.Index("ix_queue_entries_hospital_status", "hospital_id", "status"),
    )
