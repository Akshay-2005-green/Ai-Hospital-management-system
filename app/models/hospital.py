from app.extensions import db


class Hospital(db.Model):
    __tablename__ = "hospitals"

    hospital_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)

    description = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True, default=0.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )

    doctors = db.relationship(
        "Doctor",
        back_populates="hospital",
    )
    appointments = db.relationship(
        "Appointment",
        back_populates="hospital",
    )
    queue_events = db.relationship(
        "QueueEvent",
        back_populates="hospital",
    )
    ml_predictions = db.relationship(
        "MLPrediction",
        back_populates="hospital",
    )
    beds = db.relationship(
        "Bed",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
