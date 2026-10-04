from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.queue_entry import QueueEntry


receptionist_bp = Blueprint("receptionist", __name__)
ACTIVE_QUEUE_STATES = ("WAITING", "READY", "CALLED", "IN_CONSULTATION")
SCHEDULED_APPOINTMENT_STATES = ("PENDING", "SCHEDULED", "CONFIRMED", "CHECKED_IN", "IN_CONSULTATION")


def _parse_time(value):
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if not isinstance(value, str):
        return None
    for time_format in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(value.strip(), time_format).time()
        except ValueError:
            continue
    return None


def _doctor_slots(doctor, selected_date):
    if doctor.status != "AVAILABLE":
        return []

    weekday_full = selected_date.strftime("%A").lower()
    weekday_short = selected_date.strftime("%a").lower()
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor.doctor_id,
        is_available=True,
    ).all()
    matching_shifts = [
        shift for shift in availability
        if (shift.day_of_week or "").strip().lower() in {weekday_full, weekday_short}
    ]

    intervals = []
    if availability:
        intervals = [
            (shift.start_time, shift.end_time)
            for shift in matching_shifts
            if shift.start_time and shift.end_time
        ]
    elif doctor.timings:
        available_days = (doctor.available_days or "").strip().lower()
        day_aliases = {
            "mon": "monday",
            "tue": "tuesday",
            "wed": "wednesday",
            "thu": "thursday",
            "fri": "friday",
            "sat": "saturday",
            "sun": "sunday",
        }
        normalized_days = available_days.replace(" ", "")
        range_parts = normalized_days.split("-")
        in_weekday_range = False
        if len(range_parts) == 2:
            week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            first = day_aliases.get(range_parts[0][:3], range_parts[0][:3])[:3]
            last = day_aliases.get(range_parts[1][:3], range_parts[1][:3])[:3]
            if first in week and last in week:
                first_index = week.index(first)
                last_index = week.index(last)
                current_index = week.index(weekday_short)
                in_weekday_range = (
                    first_index <= current_index <= last_index
                    if first_index <= last_index
                    else current_index >= first_index or current_index <= last_index
                )
        allows_day = (
            not available_days
            or weekday_full in available_days
            or weekday_short in available_days
            or in_weekday_range
            or any(
                day_aliases.get(day, day) == weekday_full
                for day in available_days.replace(",", " ").split()
            )
        )
        if allows_day and " - " in doctor.timings:
            start, end = doctor.timings.split(" - ", 1)
            start_time = _parse_time(start)
            end_time = _parse_time(end)
            if start_time and end_time:
                intervals.append((start_time, end_time))

    booked = set()
    for appointment in Appointment.query.filter_by(
        doctor_id=doctor.doctor_id,
        appointment_date=selected_date,
    ).filter(Appointment.status != "CANCELLED"):
        occupied = _parse_time(appointment.appointment_time)
        if occupied:
            booked.add(occupied.strftime("%H:%M"))

    slots = []
    for start, end in intervals:
        cursor = datetime.combine(selected_date, start)
        finish = datetime.combine(selected_date, end)
        while cursor + timedelta(minutes=30) <= finish:
            value = cursor.strftime("%H:%M")
            if value not in booked and (
                selected_date > date.today()
                or cursor > datetime.now().replace(second=0, microsecond=0)
            ):
                slots.append({
                    "value": value,
                    "label": cursor.strftime("%I:%M %p"),
                })
            cursor += timedelta(minutes=30)
    return slots


def _doctor_is_on_duty(doctor, check_at):
    if doctor.status != "AVAILABLE":
        return False
    weekday_full = check_at.strftime("%A").lower()
    weekday_short = check_at.strftime("%a").lower()
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor.doctor_id,
        is_available=True,
    ).all()
    if availability:
        for shift in availability:
            if (shift.day_of_week or "").strip().lower() not in {weekday_full, weekday_short}:
                continue
            if shift.start_time is None or shift.end_time is None:
                return True
            if shift.start_time <= check_at.time() <= shift.end_time:
                return True
        return False

    if not doctor.timings or " - " not in doctor.timings:
        return False
    available_days = (doctor.available_days or "").lower().replace(" ", "")
    weekday = weekday_short[:3]
    if available_days:
        if "-" in available_days:
            start_day, end_day = available_days.split("-", 1)
            week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            if start_day[:3] not in week or end_day[:3] not in week:
                return False
            start_index = week.index(start_day[:3])
            end_index = week.index(end_day[:3])
            current_index = week.index(weekday)
            if start_index <= end_index:
                if not start_index <= current_index <= end_index:
                    return False
            elif current_index < start_index and current_index > end_index:
                return False
        elif weekday not in available_days:
            return False
    start_value, end_value = doctor.timings.split(" - ", 1)
    start_time = _parse_time(start_value)
    end_time = _parse_time(end_value)
    return bool(start_time and end_time and start_time <= check_at.time() <= end_time)


def _queue_number(department, hospital_id):
    from app.routes.queue import get_next_queue_number

    return get_next_queue_number(department, hospital_id)


def _create_queue_entry(appointment, emergency=False):
    entry = QueueEntry.query.filter_by(appointment_id=appointment.appointment_id).first()
    if entry:
        if emergency:
            entry.is_emergency = True
            entry.status = "WAITING"
        return entry

    department = appointment.doctor.specialization or "General"
    position = QueueEntry.query.filter(
        QueueEntry.hospital_id == appointment.hospital_id,
        QueueEntry.department == department,
        QueueEntry.status.in_(ACTIVE_QUEUE_STATES),
    ).count() + 1
    entry = QueueEntry(
        appointment=appointment,
        patient=appointment.patient,
        doctor=appointment.doctor,
        hospital=appointment.hospital,
        department=department,
        queue_number=_queue_number(department, appointment.hospital_id),
        position=position,
        status="WAITING",
        is_emergency=emergency,
    )
    db.session.add(entry)
    return entry


def _dashboard_context():
    today = date.today()
    selected_view = request.args.get("view", "today")
    search = request.args.get("q", "").strip()
    selected_date_value = request.args.get("date", today.isoformat())
    try:
        selected_date = date.fromisoformat(selected_date_value)
    except ValueError:
        selected_date = today
        selected_date_value = today.isoformat()

    appointments_query = Appointment.query
    if selected_view == "today":
        appointments_query = appointments_query.filter(Appointment.appointment_date == today)
    elif selected_view == "week":
        appointments_query = appointments_query.filter(
            Appointment.appointment_date >= today,
            Appointment.appointment_date < today + timedelta(days=7),
        )
    if search:
        appointments_query = appointments_query.join(Patient).filter(
            Patient.name.ilike(f"%{search}%")
            | Patient.phone.ilike(f"%{search}%")
            | Patient.email.ilike(f"%{search}%")
        )

    appointments = appointments_query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc(),
    ).limit(100).all()
    today_count = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.status != "CANCELLED",
    ).count()
    upcoming_count = Appointment.query.filter(
        Appointment.appointment_date >= today,
        Appointment.status.in_(SCHEDULED_APPOINTMENT_STATES),
    ).count()
    emergency_count = QueueEntry.query.filter(
        QueueEntry.is_emergency.is_(True),
        QueueEntry.status.in_(ACTIVE_QUEUE_STATES),
    ).count()
    active_queue_count = QueueEntry.query.filter(
        QueueEntry.status.in_(ACTIVE_QUEUE_STATES),
    ).count()
    doctors = Doctor.query.order_by(Doctor.name.asc()).all()
    patients = Patient.query.order_by(Patient.name.asc()).all()
    hospitals = Hospital.query.order_by(Hospital.name.asc()).all()
    selected_doctor_id = request.args.get("doctor_id", type=int)
    selected_doctor = db.session.get(Doctor, selected_doctor_id) if selected_doctor_id else None
    slots = _doctor_slots(selected_doctor, selected_date) if selected_doctor else []
    return {
        "receptionist_name": session.get("receptionist_name", "Reception Desk"),
        "appointments": appointments,
        "today_count": today_count,
        "upcoming_count": upcoming_count,
        "emergency_count": emergency_count,
        "active_queue_count": active_queue_count,
        "doctors": doctors,
        "patients": patients,
        "hospitals": hospitals,
        "selected_view": selected_view,
        "search": search,
        "selected_date": selected_date_value,
        "selected_doctor_id": selected_doctor_id,
        "slots": slots,
    }


@receptionist_bp.route("/receptionist-dashboard")
def dashboard():
    if session.get("role") != "receptionist":
        return redirect(url_for("auth.login"))

    return render_template("receptionist_dashboard.html", **_dashboard_context())


@receptionist_bp.route("/receptionist/appointments", methods=["POST"])
def create_appointment():
    if session.get("role") != "receptionist":
        return redirect(url_for("auth.login"))

    patient_mode = request.form.get("patient_mode", "existing")
    patient = None
    if patient_mode == "existing":
        patient = db.session.get(Patient, request.form.get("patient_id", type=int))
        if patient is None:
            flash("Select a registered patient.", "error")
            return redirect(url_for("receptionist.dashboard"))
    elif patient_mode == "new":
        name = request.form.get("new_patient_name", "").strip()
        email = request.form.get("new_patient_email", "").strip().lower()
        phone = request.form.get("new_patient_phone", "").strip()
        if not name or not email or not phone:
            flash("A walk-in patient needs a name, email, and phone number.", "error")
            return redirect(url_for("receptionist.dashboard"))
        if Patient.query.filter((Patient.email == email) | (Patient.phone == phone)).first():
            flash("That email or phone number is already registered. Select the existing patient instead.", "error")
            return redirect(url_for("receptionist.dashboard"))
        patient = Patient(name=name, email=email, phone=phone, password_hash="")
        db.session.add(patient)
        db.session.flush()
    else:
        flash("Choose an existing or new patient.", "error")
        return redirect(url_for("receptionist.dashboard"))

    doctor = db.session.get(Doctor, request.form.get("doctor_id", type=int))
    if doctor is None:
        db.session.rollback()
        flash("Select a valid doctor.", "error")
        return redirect(url_for("receptionist.dashboard"))

    emergency = request.form.get("is_emergency") == "yes"
    reason = request.form.get("reason", "").strip()
    if len(reason) > 500:
        db.session.rollback()
        flash("Keep the visit reason under 500 characters.", "error")
        return redirect(url_for("receptionist.dashboard"))
    if emergency:
        if not _doctor_is_on_duty(doctor, datetime.now()):
            db.session.rollback()
            flash("No selected doctor is on duty at this time. Contact emergency services or the hospital's emergency department for immediate care.", "error")
            return redirect(url_for("receptionist.dashboard"))
        appointment_date = date.today()
        appointment_time = datetime.now().strftime("%H:%M")
        status = "CHECKED_IN"
    else:
        try:
            appointment_date = date.fromisoformat(request.form.get("appointment_date", ""))
        except ValueError:
            db.session.rollback()
            flash("Choose a valid appointment date.", "error")
            return redirect(url_for("receptionist.dashboard"))
        slots = _doctor_slots(doctor, appointment_date)
        appointment_time = request.form.get("appointment_time", "")
        if not any(slot["value"] == appointment_time for slot in slots):
            db.session.rollback()
            flash("That time is outside the doctor's available, unbooked hours.", "error")
            return redirect(url_for(
                "receptionist.dashboard",
                date=appointment_date.isoformat(),
                doctor_id=doctor.doctor_id,
            ))
        status = "CONFIRMED"

    appointment = Appointment(
        patient=patient,
        doctor=doctor,
        hospital=doctor.hospital,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        consultation_type="IN_PERSON",
        status=status,
        reason=reason,
    )
    db.session.add(appointment)
    db.session.flush()
    if emergency:
        _create_queue_entry(appointment, emergency=True)
    db.session.commit()

    if emergency:
        flash(
            f"Emergency arrival registered as {appointment.queue_entry.queue_number} and placed at the front of the clinician queue. This does not replace emergency services.",
            "success",
        )
    else:
        flash("Appointment scheduled successfully.", "success")
    return redirect(url_for("receptionist.dashboard"))


@receptionist_bp.route("/receptionist/appointments/<int:appointment_id>/<action>", methods=["POST"])
def update_appointment(appointment_id, action):
    if session.get("role") != "receptionist":
        return redirect(url_for("auth.login"))
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        flash("Appointment not found.", "error")
        return redirect(url_for("receptionist.dashboard"))

    if action == "check-in":
        if appointment.status == "CANCELLED":
            flash("A cancelled appointment cannot be checked in.", "error")
        else:
            appointment.status = "CHECKED_IN"
            _create_queue_entry(appointment)
            db.session.commit()
            flash(f"{appointment.patient.name} checked in as {appointment.queue_entry.queue_number}.", "success")
    elif action == "cancel":
        appointment.status = "CANCELLED"
        if appointment.queue_entry:
            appointment.queue_entry.status = "CANCELLED"
        db.session.commit()
        flash("Appointment cancelled.", "success")
    else:
        return "Unknown appointment action", 404
    return redirect(url_for("receptionist.dashboard"))
