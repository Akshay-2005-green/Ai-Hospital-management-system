from datetime import datetime
from app.extensions import db


class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    medical_record_id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id"),
        nullable=True,
        index=True,
    )

    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)

    diagnosis = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    patient = db.relationship(
        "Patient",
        back_populates="medical_records",
    )
    doctor = db.relationship(
        "Doctor",
        back_populates="medical_records",
    )
