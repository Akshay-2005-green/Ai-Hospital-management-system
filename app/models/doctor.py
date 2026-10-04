from app.extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=True, default="General")
    status = db.Column(
        db.String(20),
        nullable=False,
        default="AVAILABLE",
        info={"validators": ["AVAILABLE", "BUSY", "OFFLINE", "ON_LEAVE"]},
    )

    experience = db.Column(db.Integer, nullable=True, default=0)
    qualification = db.Column(db.String(200), nullable=True)
    consultation_fee = db.Column(db.Integer, nullable=True)

    available_days = db.Column(db.String(100), nullable=True)
    timings = db.Column(db.String(100), nullable=True)

    rating = db.Column(db.Float, nullable=True, default=0.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('AVAILABLE', 'BUSY', 'OFFLINE', 'ON_LEAVE')",
            name="doctor_status_valid",
        ),
    )

    hospital = db.relationship(
        "Hospital",
        back_populates="doctors",
    )
    appointments = db.relationship(
        "Appointment",
        back_populates="doctor",
    )
    availability = db.relationship(
        "DoctorAvailability",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    queue_events = db.relationship(
        "QueueEvent",
        back_populates="doctor",
    )
    queue_entries = db.relationship(
        "QueueEntry",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    medical_records = db.relationship(
        "MedicalRecord",
        back_populates="doctor",
    )
    ml_predictions = db.relationship(
        "MLPrediction",
        back_populates="doctor",
    )
