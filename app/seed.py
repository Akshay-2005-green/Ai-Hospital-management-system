from datetime import date

from app.extensions import db
from app.models import (
    Appointment,
    Doctor,
    Hospital,
    MLPrediction,
    MedicalRecord,
    Patient,
    QueueEntry,
    QueueEvent,
)


def seed_sample_data():
    """Create a minimal sample record set used by the model tests."""
    hospital = Hospital.query.filter_by(name="H1").first()
    if hospital is None:
        hospital = Hospital(name="H1", location="Lucknow")
        db.session.add(hospital)
        db.session.flush()

    doctor = Doctor.query.filter_by(hospital_id=hospital.hospital_id, name="D1").first()
    if doctor is None:
        doctor = Doctor(
            hospital=hospital,
            name="D1",
            specialization="Cardiology",
            status="AVAILABLE",
        )
        db.session.add(doctor)
        db.session.flush()

    patient = Patient.query.filter_by(email="p1@example.com").first()
    if patient is None:
        patient = Patient(
            name="P1",
            email="p1@example.com",
            password_hash="hash",
            phone="9876543210",
            date_of_birth=date(1990, 1, 1),
        )
        db.session.add(patient)
        db.session.flush()

    appointment = Appointment.query.filter_by(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        hospital_id=hospital.hospital_id,
    ).first()
    if appointment is None:
        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            hospital=hospital,
            appointment_date=date.today(),
            appointment_time="09:00 AM",
            status="PENDING",
            consultation_type="IN_PERSON",
        )
        db.session.add(appointment)
        db.session.flush()

    queue_entry = QueueEntry.query.filter_by(appointment_id=appointment.appointment_id).first()
    if queue_entry is None:
        queue_entry = QueueEntry(
            appointment=appointment,
            patient=patient,
            doctor=doctor,
            hospital=hospital,
            department="Cardiology",
            queue_number="Q-1",
            position=1,
            status="WAITING",
        )
        db.session.add(queue_entry)
        db.session.flush()

    queue_event = QueueEvent.query.filter_by(hospital_id=hospital.hospital_id).first()
    if queue_event is None:
        queue_event = QueueEvent(
            hospital=hospital,
            doctor=doctor,
            queue_entry=queue_entry,
            event_type="CHECKED_IN",
            event_data={"queue_number": queue_entry.queue_number},
        )
        db.session.add(queue_event)
        db.session.flush()

    medical_record = MedicalRecord.query.filter_by(patient_id=patient.patient_id).first()
    if medical_record is None:
        medical_record = MedicalRecord(
            patient=patient,
            doctor=doctor,
            filename="report.pdf",
            filepath="/tmp/report.pdf",
            file_type="pdf",
            diagnosis="Stable",
            notes="Follow up in 2 weeks.",
        )
        db.session.add(medical_record)
        db.session.flush()

    ml_prediction = MLPrediction.query.filter_by(patient_id=patient.patient_id).first()
    if ml_prediction is None:
        ml_prediction = MLPrediction(
            hospital=hospital,
            doctor=doctor,
            patient=patient,
            model_name="triage_model",
            prediction_type="risk_score",
            input_data={"age": 42},
            prediction={"risk": "low"},
            confidence=0.92,
        )
        db.session.add(ml_prediction)

    db.session.commit()
    return hospital
