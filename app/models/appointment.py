from datetime import datetime

from sqlalchemy.orm import validates

from app.extensions import db
from app.models.enums import AppointmentStatus, ConsultationType


class Appointment(db.Model):
    __tablename__ = "appointments"

    appointment_id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id"),
        nullable=False,
        index=True,
    )
    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=False,
        index=True,
    )

    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.String(20), nullable=False)

    consultation_type = db.Column(
        db.String(50),
        nullable=False,
        default=ConsultationType.IN_PERSON.value,
    )
    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING",
    )

    reason = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('PENDING', 'SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'IN_CONSULTATION', 'COMPLETED', 'CANCELLED', 'NO_SHOW')",
            name="appointment_status_valid",
        ),
    )

    @validates("appointment_time")
    def validate_appointment_time(self, key, value):
        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")
        return value

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    hospital = db.relationship("Hospital", back_populates="appointments")

    queue_entry = db.relationship(
        "QueueEntry",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan",
    )
