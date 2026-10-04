from datetime import datetime
from app.extensions import db


class QueueEvent(db.Model):
    __tablename__ = "queue_events"

    queue_event_id = db.Column(db.Integer, primary_key=True)

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=False,
        index=True,
    )
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id"),
        nullable=True,
        index=True,
    )
    queue_entry_id = db.Column(
        db.Integer,
        db.ForeignKey("queue_entries.queue_entry_id"),
        nullable=True,
        index=True,
    )

    event_type = db.Column(db.String(50), nullable=False)
    event_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    event_data = db.Column(db.JSON, nullable=True)

    hospital = db.relationship(
        "Hospital",
        back_populates="queue_events",
    )
    doctor = db.relationship(
        "Doctor",
        back_populates="queue_events",
    )
    queue_entry = db.relationship("QueueEntry")
