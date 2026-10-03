from app.extensions import db
from app.models.base import CreatedAtMixin, ReprMixin


class Hospital(ReprMixin, CreatedAtMixin, db.Model):
    __tablename__ = "hospitals"

    hospital_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255))
    contact_number = db.Column(db.String(30))

    # Relationships (1:N)
    doctors = db.relationship("Doctor", back_populates="hospital")
    appointments = db.relationship("Appointment", back_populates="hospital")
    queue_entries = db.relationship("QueueEntry", back_populates="hospital")
    doctor_availabilities = db.relationship("DoctorAvailability", back_populates="hospital")
    queue_events = db.relationship("QueueEvent", back_populates="hospital")
    ml_predictions = db.relationship("MLPrediction", back_populates="hospital")
