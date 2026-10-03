from datetime import date, datetime, time, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Appointment, Doctor, Hospital, Patient, QueueEntry
from app.seed import seed_sample_data


def _basics():
    hospital = Hospital(name="H1")
    patient = Patient(name="P1", email="p1@example.com")
    doctor = Doctor(hospital=hospital, name="D1")
    appt = Appointment(
        patient=patient, doctor=doctor, hospital=hospital,
        appointment_date=date.today(), appointment_time=time(9, 0),
    )
    db.session.add_all([hospital, patient, doctor, appt])
    db.session.commit()
    return hospital, patient, doctor, appt


def test_seed_connects_all_entities(app):
    seed_sample_data()
    hospital = Hospital.query.one()
    assert len(hospital.doctors) == 1
    assert len(hospital.appointments) == 1
    assert len(hospital.queue_events) == 1
    assert len(hospital.ml_predictions) == 1
    appt = hospital.appointments[0]
    assert appt.queue_entry.queue_position == 1
    assert appt.patient.medical_records[0].doctor is hospital.doctors[0]


def test_defaults(app):
    _, _, doctor, appt = _basics()
    assert doctor.status == "AVAILABLE"
    assert appt.status == "PENDING"
    assert appt.created_at is not None and appt.updated_at is not None


def test_patient_email_unique(app):
    db.session.add_all([Patient(name="A", email="x@y.z"), Patient(name="B", email="x@y.z")])
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_one_queue_entry_per_appointment(app):
    hospital, patient, doctor, appt = _basics()
    for _ in range(2):
        db.session.add(QueueEntry(appointment=appt, patient=patient, doctor=doctor, hospital=hospital))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_invalid_status_rejected(app):
    hospital = Hospital(name="H")
    db.session.add(Doctor(hospital=hospital, name="D", status="NOT_A_STATUS"))
    with pytest.raises(IntegrityError):
        db.session.commit()
