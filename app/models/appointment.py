from app.extensions import db
from app.models.base import ReprMixin, TimestampMixin, enum_check
from app.models.enums import AppointmentStatus


class Appointment(ReprMixin, TimestampMixin, db.Model):
    __tablename__ = "appointments"

    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False, index=True
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False, index=True
    )
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(
        db.String(20), nullable=False, default=AppointmentStatus.PENDING.value, index=True
    )

    # Relationships
    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    hospital = db.relationship("Hospital", back_populates="appointments")
    # MVP: one *current* queue entry per appointment (1:1).
    queue_entry = db.relationship(
        "QueueEntry", back_populates="appointment", uselist=False
    )
    queue_events = db.relationship("QueueEvent", back_populates="appointment")
    medical_records = db.relationship("MedicalRecord", back_populates="appointment")

    __table_args__ = (
        enum_check("status", AppointmentStatus, "ck_appointments_status"),
        db.Index("ix_appointments_doctor_date", "doctor_id", "appointment_date"),
        db.Index("ix_appointments_hospital_date", "hospital_id", "appointment_date"),
    )
