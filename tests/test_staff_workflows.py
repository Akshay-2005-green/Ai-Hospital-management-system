from datetime import date, datetime, time, timedelta

from app.extensions import db
from app.models import Appointment, Doctor, Hospital, Patient, QueueEntry
from app.models.doctor_availability import DoctorAvailability


def _create_staff_booking_fixture(weekday=None):
    hospital = Hospital(name="Front Desk Hospital", location="Test")
    doctor = Doctor(
        hospital=hospital,
        name="Dr. Shift",
        specialization="General",
        status="AVAILABLE",
    )
    patient = Patient(
        name="Scheduled Patient",
        email="scheduled@example.test",
        phone="5551234500",
        password_hash="",
    )
    db.session.add_all([hospital, doctor, patient])
    db.session.flush()
    if weekday is not None:
        db.session.add(DoctorAvailability(
            doctor_id=doctor.doctor_id,
            day_of_week=weekday,
            start_time=time(0, 0),
            end_time=time(23, 59),
            is_available=True,
        ))
    db.session.commit()
    return hospital, doctor, patient


def _login_receptionist(client):
    with client.session_transaction() as session:
        session["role"] = "receptionist"
        session["receptionist_id"] = 1


def _login_doctor(client, doctor_id):
    with client.session_transaction() as session:
        session["role"] = "doctor"
        session["doctor_id"] = doctor_id


def test_receptionist_can_book_only_doctor_shift_slots(app):
    future_date = date.today() + timedelta(days=7)
    weekday = future_date.strftime("%A")
    _hospital, doctor, patient = _create_staff_booking_fixture(weekday)
    client = app.test_client()
    _login_receptionist(client)

    response = client.post(
        "/receptionist/appointments",
        data={
            "patient_mode": "existing",
            "patient_id": patient.patient_id,
            "doctor_id": doctor.doctor_id,
            "appointment_date": future_date.isoformat(),
            "appointment_time": "09:00",
        },
    )

    assert response.status_code == 302
    appointment = Appointment.query.one()
    assert appointment.appointment_date == future_date
    assert appointment.status == "CONFIRMED"


def test_receptionist_cannot_double_book_a_doctor_time(app):
    future_date = date.today() + timedelta(days=7)
    _hospital, doctor, patient = _create_staff_booking_fixture(future_date.strftime("%A"))
    other_patient = Patient(
        name="Second Patient",
        email="second@example.test",
        phone="5551234501",
        password_hash="",
    )
    db.session.add(other_patient)
    db.session.add(Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        hospital_id=doctor.hospital_id,
        appointment_date=future_date,
        appointment_time="09:00",
        status="CONFIRMED",
    ))
    db.session.commit()
    client = app.test_client()
    _login_receptionist(client)

    response = client.post(
        "/receptionist/appointments",
        data={
            "patient_mode": "existing",
            "patient_id": other_patient.patient_id,
            "doctor_id": doctor.doctor_id,
            "appointment_date": future_date.isoformat(),
            "appointment_time": "09:00",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"outside the doctor" in response.data
    assert Appointment.query.count() == 1


def test_receptionist_emergency_walkin_is_created_in_priority_queue(app):
    today_weekday = date.today().strftime("%A")
    _hospital, doctor, _patient = _create_staff_booking_fixture(today_weekday)
    client = app.test_client()
    _login_receptionist(client)

    response = client.post(
        "/receptionist/appointments",
        data={
            "patient_mode": "new",
            "new_patient_name": "Emergency Walkin",
            "new_patient_email": "walkin@example.test",
            "new_patient_phone": "5551234502",
            "doctor_id": doctor.doctor_id,
            "is_emergency": "yes",
            "reason": "Needs immediate clinical assessment",
        },
    )

    assert response.status_code == 302
    appointment = Appointment.query.filter_by(patient_id=Patient.query.filter_by(
        email="walkin@example.test"
    ).one().patient_id).one()
    assert appointment.appointment_date == date.today()
    assert appointment.status == "CHECKED_IN"
    assert appointment.queue_entry is not None
    assert appointment.queue_entry.is_emergency is True
    assert appointment.queue_entry.status == "WAITING"


def test_doctor_can_progress_only_their_assigned_queue_case(app):
    hospital, doctor, patient = _create_staff_booking_fixture(date.today().strftime("%A"))
    appointment = Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        hospital_id=hospital.hospital_id,
        appointment_date=date.today(),
        appointment_time=datetime.now().strftime("%H:%M"),
        status="CHECKED_IN",
    )
    db.session.add(appointment)
    db.session.flush()
    entry = QueueEntry(
        appointment=appointment,
        patient=patient,
        doctor=doctor,
        hospital=hospital,
        department="General",
        queue_number="A-001",
        position=1,
        status="WAITING",
        is_emergency=True,
    )
    db.session.add(entry)
    db.session.commit()

    client = app.test_client()
    _login_doctor(client, doctor.doctor_id)
    for expected in ("CALLED", "IN_CONSULTATION", "COMPLETED"):
        response = client.post(f"/doctor/queue/{entry.queue_entry_id}/advance")
        assert response.status_code == 302
        db.session.refresh(entry)
        assert entry.status == expected

    assert appointment.status == "COMPLETED"


def test_receptionist_call_next_selects_priority_arrival_first(app):
    hospital, doctor, first_patient = _create_staff_booking_fixture(date.today().strftime("%A"))
    second_patient = Patient(
        name="Urgent Patient",
        email="urgent@example.test",
        phone="5551234503",
        password_hash="",
    )
    db.session.add(second_patient)
    db.session.flush()
    appointments = []
    for patient in (first_patient, second_patient):
        appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=doctor.doctor_id,
            hospital_id=hospital.hospital_id,
            appointment_date=date.today(),
            appointment_time=datetime.now().strftime("%H:%M"),
            status="CHECKED_IN",
        )
        db.session.add(appointment)
        db.session.flush()
        appointments.append(appointment)

    routine_entry = QueueEntry(
        appointment=appointments[0],
        patient=first_patient,
        doctor=doctor,
        hospital=hospital,
        department="General",
        queue_number="A-001",
        position=1,
        status="WAITING",
    )
    emergency_entry = QueueEntry(
        appointment=appointments[1],
        patient=second_patient,
        doctor=doctor,
        hospital=hospital,
        department="General",
        queue_number="A-002",
        position=2,
        status="WAITING",
        is_emergency=True,
    )
    db.session.add_all([routine_entry, emergency_entry])
    db.session.commit()

    client = app.test_client()
    _login_receptionist(client)
    response = client.post("/api/queue/call-next", json={"department": "General"})

    assert response.status_code == 200
    assert response.get_json()["queue_number"] == "A-002"


def test_receptionist_and_doctor_dashboards_render_their_workflows(app):
    _hospital, doctor, _patient = _create_staff_booking_fixture()
    receptionist_client = app.test_client()
    _login_receptionist(receptionist_client)
    reception_response = receptionist_client.get("/receptionist-dashboard")
    assert reception_response.status_code == 200
    assert b"Add appointment or urgent arrival" in reception_response.data
    assert b"Appointments" in reception_response.data

    doctor_client = app.test_client()
    _login_doctor(doctor_client, doctor.doctor_id)
    doctor_response = doctor_client.get("/doctor-dashboard")
    assert doctor_response.status_code == 200
    assert b"Live patient queue" in doctor_response.data
    assert b"today's schedule" in doctor_response.data.lower()


def test_doctor_can_set_and_disable_a_weekday_shift(app):
    _hospital, doctor, _patient = _create_staff_booking_fixture()
    client = app.test_client()
    _login_doctor(client, doctor.doctor_id)

    response = client.post(
        "/doctor/availability",
        data={
            "day_of_week": "Monday",
            "start_time": "08:30",
            "end_time": "16:30",
            "is_available": "yes",
        },
    )
    assert response.status_code == 302
    shift = DoctorAvailability.query.filter_by(
        doctor_id=doctor.doctor_id,
        day_of_week="Monday",
    ).one()
    assert shift.is_available is True
    assert shift.start_time == time(8, 30)
    assert shift.end_time == time(16, 30)

    client.post(
        "/doctor/availability",
        data={"day_of_week": "Monday"},
    )
    db.session.refresh(shift)
    assert shift.is_available is False
    assert shift.start_time is None


def test_doctor_cannot_save_invalid_or_overnight_shift(app):
    _hospital, doctor, _patient = _create_staff_booking_fixture()
    client = app.test_client()
    _login_doctor(client, doctor.doctor_id)

    response = client.post(
        "/doctor/availability",
        data={
            "day_of_week": "Monday",
            "start_time": "17:00",
            "end_time": "09:00",
            "is_available": "yes",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Shift end time must be later" in response.data
    assert DoctorAvailability.query.count() == 0
