from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin, enum_check
from app.models.enums import AvailabilityStatus


class DoctorAvailability(ReprMixin, CreatedAtMixin, db.Model):
    __tablename__ = "doctor_availability"

    availability_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False, index=True
    )
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    status = db.Column(db.String(20), nullable=False, default=AvailabilityStatus.AVAILABLE.value)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    reason = db.Column(db.String(255))

    # Relationships
    doctor = db.relationship("Doctor", back_populates="availabilities")
    hospital = db.relationship("Hospital", back_populates="doctor_availabilities")

    __table_args__ = (
        enum_check("status", AvailabilityStatus, "ck_doctor_availability_status"),
        db.Index("ix_doctor_availability_doctor_start", "doctor_id", "start_time"),
    )
