from datetime import datetime
from app.extensions import db


class MLPrediction(db.Model):
    __tablename__ = "ml_predictions"

    prediction_id = db.Column(db.Integer, primary_key=True)

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=True,
        index=True,
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id"),
        nullable=True,
        index=True,
    )
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id"),
        nullable=True,
        index=True,
    )

    model_name = db.Column(db.String(150), nullable=False)
    prediction_type = db.Column(db.String(100), nullable=False)

    input_data = db.Column(db.JSON, nullable=True)
    prediction = db.Column(db.JSON, nullable=True)
    confidence = db.Column(db.Float, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    hospital = db.relationship(
        "Hospital",
        back_populates="ml_predictions",
    )
    doctor = db.relationship(
        "Doctor",
        back_populates="ml_predictions",
    )
    patient = db.relationship(
        "Patient",
        back_populates="ml_predictions",
    )
