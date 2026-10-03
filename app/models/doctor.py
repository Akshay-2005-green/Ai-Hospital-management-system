from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin, enum_check
from app.models.enums import DoctorStatus


class Doctor(ReprMixin, CreatedAtMixin, db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(100))
    department = db.Column(db.String(100))
    status = db.Column(
        db.String(20), nullable=False, default=DoctorStatus.AVAILABLE.value, index=True
    )

    # Relationships
    hospital = db.relationship("Hospital", back_populates="doctors")
    appointments = db.relationship("Appointment", back_populates="doctor")
    queue_entries = db.relationship("QueueEntry", back_populates="doctor")
    availabilities = db.relationship("DoctorAvailability", back_populates="doctor")
    queue_events = db.relationship("QueueEvent", back_populates="doctor")
    medical_records = db.relationship("MedicalRecord", back_populates="doctor")
    ml_predictions = db.relationship("MLPrediction", back_populates="doctor")

    __table_args__ = (enum_check("status", DoctorStatus, "ck_doctors_status"),)
