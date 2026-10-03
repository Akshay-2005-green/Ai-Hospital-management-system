"""Import every model so SQLAlchemy/Alembic see the full, connected schema.

Build order (see README): Hospital/Patient/Doctor -> Appointment/QueueEntry ->
DoctorAvailability/QueueEvent -> MedicalRecord -> MLPrediction.
"""
from app.models.enums import (
    AppointmentStatus,
    AvailabilityStatus,
    DoctorStatus,
    LoadLevel,
    PredictionType,
    QueueEventType,
    QueueStatus,
)
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.queue_entry import QueueEntry
from app.models.doctor_availability import DoctorAvailability
from app.models.queue_event import QueueEvent
from app.models.medical_record import MedicalRecord
from app.models.ml_prediction import MLPrediction

__all__ = [
    "Hospital", "Patient", "Doctor", "Appointment", "QueueEntry",
    "DoctorAvailability", "QueueEvent", "MedicalRecord", "MLPrediction",
    "AppointmentStatus", "AvailabilityStatus", "DoctorStatus", "LoadLevel",
    "PredictionType", "QueueEventType", "QueueStatus",
]
