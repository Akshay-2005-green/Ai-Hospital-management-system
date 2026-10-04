from datetime import time
from app.extensions import db


class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availability"

    availability_id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id"),
        nullable=False,
        index=True,
    )

    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    is_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    doctor = db.relationship(
        "Doctor",
        back_populates="availability",
    )
