from datetime import datetime
from app.extensions import db
from app.models.enums import NotificationType


class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    notification_type = db.Column(
        db.String(50),
        nullable=False,
        default=NotificationType.GENERAL.value,
    )

    is_read = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    patient = db.relationship(
        "Patient",
        back_populates="notifications",
    )
