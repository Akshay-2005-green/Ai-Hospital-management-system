from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin


class MedicalRecord(ReprMixin, CreatedAtMixin, db.Model):
    __tablename__ = "medical_records"

    record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False, index=True
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False, index=True
    )
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.appointment_id"), index=True
    )
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    medications = db.Column(db.Text)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationships
    patient = db.relationship("Patient", back_populates="medical_records")
    doctor = db.relationship("Doctor", back_populates="medical_records")
    appointment = db.relationship("Appointment", back_populates="medical_records")
