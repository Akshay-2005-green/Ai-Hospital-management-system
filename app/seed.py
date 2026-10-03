"""Sample data that exercises every relationship (development only)."""
from datetime import date, datetime, time, timezone

from app.extensions import db
from app.models import (
    Appointment, AppointmentStatus, Doctor, Hospital, LoadLevel, MedicalRecord,
    MLPrediction, Patient, PredictionType, QueueEntry, QueueEvent, QueueEventType,
    DoctorAvailability, AvailabilityStatus,
)


def seed_sample_data() -> None:
    now = datetime.now(timezone.utc)

    hospital = Hospital(name="City General Hospital", location="Kanpur", contact_number="0512-000000")
    patient = Patient(name="Asha Verma", email="asha@example.com", gender="F", date_of_birth=date(1995, 4, 12))
    doctor = Doctor(hospital=hospital, name="Dr. R. Singh", specialization="Cardiology", department="OPD")

    appointment = Appointment(
        patient=patient, doctor=doctor, hospital=hospital,
        appointment_date=date.today(), appointment_time=time(10, 30),
        reason="Chest discomfort", status=AppointmentStatus.APPROVED.value,
    )
    queue_entry = QueueEntry(
        appointment=appointment, patient=patient, doctor=doctor, hospital=hospital,
        queue_position=1, estimated_wait_time=12.5,
    )
    event = QueueEvent(
        hospital=hospital, doctor=doctor, appointment=appointment, queue_entry=queue_entry,
        event_type=QueueEventType.PATIENT_JOINED.value, event_time=now,
    )
    availability = DoctorAvailability(
        doctor=doctor, hospital=hospital, status=AvailabilityStatus.AVAILABLE.value, start_time=now,
    )
    record = MedicalRecord(patient=patient, doctor=doctor, appointment=appointment, symptoms="Chest pain")
    prediction = MLPrediction(
        hospital=hospital, doctor=doctor, prediction_type=PredictionType.WAIT_TIME.value,
        queue_size=1, doctors_available=1, emergency_cases=0, appointments_count=1,
        avg_consultation_time=15.0, predicted_wait_time=12.5,
        predicted_load=LoadLevel.LOW.value, model_version="v0.1.0", prediction_time=now,
    )

    db.session.add_all([hospital, patient, doctor, appointment, queue_entry,
                        event, availability, record, prediction])
    db.session.commit()
