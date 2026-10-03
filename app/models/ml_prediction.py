from app.extensions import db
from app.models.base import ReprMixin, enum_check
from app.models.enums import LoadLevel, PredictionType


class MLPrediction(ReprMixin, db.Model):
    """Stored model inputs + outputs, versioned for traceability."""

    __tablename__ = "ml_predictions"

    prediction_id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(
        db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False, index=True
    )
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), index=True)
    prediction_type = db.Column(db.String(20), nullable=False)

    # Model inputs
    queue_size = db.Column(db.Integer)
    doctors_available = db.Column(db.Integer)
    emergency_cases = db.Column(db.Integer)
    appointments_count = db.Column(db.Integer)
    avg_consultation_time = db.Column(db.Float)

    # Model outputs
    predicted_wait_time = db.Column(db.Float)  # minutes
    predicted_load = db.Column(db.String(10))
    model_version = db.Column(db.String(50))
    prediction_time = db.Column(db.DateTime, nullable=False, index=True)

    # Relationships
    hospital = db.relationship("Hospital", back_populates="ml_predictions")
    doctor = db.relationship("Doctor", back_populates="ml_predictions")

    __table_args__ = (
        enum_check("prediction_type", PredictionType, "ck_ml_predictions_type"),
        enum_check("predicted_load", LoadLevel, "ck_ml_predictions_load"),
        db.Index("ix_ml_predictions_hospital_time", "hospital_id", "prediction_time"),
    )
