from datetime import date, datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.doctor_availability import DoctorAvailability
from app.models.patient import Patient
from app.models.queue_entry import QueueEntry


doctor_bp = Blueprint("doctor", __name__)
ACTIVE_QUEUE_STATES = ("WAITING", "READY", "CALLED", "IN_CONSULTATION")


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@doctor_bp.route("/doctor-dashboard")
def dashboard():
    if session.get("role") != "doctor":
        return redirect(url_for("auth.login"))

    doctor_id = session.get("doctor_id")
    today = date.today()
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == today,
        Appointment.status.notin_(("CANCELLED", "COMPLETED", "NO_SHOW")),
    ).order_by(Appointment.appointment_time.asc()).all()
    queue_entries = QueueEntry.query.filter(
        QueueEntry.doctor_id == doctor_id,
        QueueEntry.status.in_(ACTIVE_QUEUE_STATES),
    ).order_by(
        QueueEntry.is_emergency.desc(),
        QueueEntry.position.asc(),
        QueueEntry.joined_at.asc(),
    ).all()
    doctor = db.session.get(Doctor, doctor_id)
    availability = []
    if doctor is not None:
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
        ).order_by(DoctorAvailability.day_of_week.asc()).all()
    active_patients = Patient.query.count()
    appointments_count = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= today,
        Appointment.status.notin_(("CANCELLED", "COMPLETED", "NO_SHOW")),
    ).count()

    return render_template(
        "doctor_dashboard.html",
        doctor_name=session.get("doctor_name", "Doctor"),
        today=today.strftime("%A, %d %B %Y"),
        active_patients=active_patients,
        appointments_count=appointments_count,
        queue_count=len(queue_entries),
        appointments=appointments,
        queue_entries=queue_entries,
        availability=availability,
        doctor_exists=doctor is not None,
    )


@doctor_bp.route("/doctor/availability", methods=["POST"])
def update_availability():
    if session.get("role") != "doctor":
        return redirect(url_for("auth.login"))

    doctor = db.session.get(Doctor, session.get("doctor_id"))
    if doctor is None:
        flash("No doctor profile is linked to this account.", "error")
        return redirect(url_for("doctor.dashboard"))

    day = request.form.get("day_of_week", "").strip()
    valid_days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    if day not in valid_days:
        flash("Select a valid weekday.", "error")
        return redirect(url_for("doctor.dashboard"))

    is_available = request.form.get("is_available") == "yes"
    if is_available:
        try:
            start_time = datetime.strptime(request.form.get("start_time", ""), "%H:%M").time()
            end_time = datetime.strptime(request.form.get("end_time", ""), "%H:%M").time()
        except ValueError:
            flash("Enter valid shift start and end times.", "error")
            return redirect(url_for("doctor.dashboard"))
        if start_time >= end_time:
            flash("Shift end time must be later than the start time.", "error")
            return redirect(url_for("doctor.dashboard"))

    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor.doctor_id,
        day_of_week=day,
    ).first()
    if availability is None:
        availability = DoctorAvailability(
            doctor_id=doctor.doctor_id,
            day_of_week=day,
        )
        db.session.add(availability)

    if is_available:
        availability.start_time = start_time
        availability.end_time = end_time
        availability.is_available = True
        flash(f"{day} shift saved.", "success")
    else:
        availability.start_time = None
        availability.end_time = None
        availability.is_available = False
        flash(f"{day} marked unavailable.", "success")

    db.session.commit()
    return redirect(url_for("doctor.dashboard"))


@doctor_bp.route("/doctor/queue/<int:queue_id>/advance", methods=["POST"])
def advance_queue(queue_id):
    if session.get("role") != "doctor":
        return redirect(url_for("auth.login"))

    queue_entry = db.session.get(QueueEntry, queue_id)
    if queue_entry is None or queue_entry.doctor_id != session.get("doctor_id"):
        flash("Queue entry not found for your doctor account.", "error")
        return redirect(url_for("doctor.dashboard"))

    next_states = {
        "WAITING": "CALLED",
        "READY": "CALLED",
        "CALLED": "IN_CONSULTATION",
        "IN_CONSULTATION": "COMPLETED",
    }
    transition = next_states.get(queue_entry.status)
    if transition is None:
        flash("This queue entry cannot be advanced from its current status.", "error")
        return redirect(url_for("doctor.dashboard"))

    new_status = transition
    queue_entry.status = new_status
    if new_status == "CALLED":
        queue_entry.called_at = _utcnow()
        queue_entry.appointment.status = "CHECKED_IN"
    elif new_status == "IN_CONSULTATION":
        queue_entry.consultation_started_at = _utcnow()
        queue_entry.appointment.status = "IN_CONSULTATION"
    else:
        queue_entry.completed_at = _utcnow()
        queue_entry.appointment.status = "COMPLETED"
    db.session.commit()
    flash(f"{queue_entry.queue_number} updated to {new_status.replace('_', ' ').title()}.", "success")
    return redirect(url_for("doctor.dashboard"))
