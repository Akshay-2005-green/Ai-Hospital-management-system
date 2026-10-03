from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin


class Patient(ReprMixin, CreatedAtMixin, db.Model):
    __tablename__ = "patients"

    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(30))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))

    # Relationships (1:N)
    appointments = db.relationship("Appointment", back_populates="patient")
    queue_entries = db.relationship("QueueEntry", back_populates="patient")
    medical_records = db.relationship("MedicalRecord", back_populates="patient")
