from datetime import datetime, date, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from sqlalchemy import or_

from app.extensions import db

from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.notification import Notification


appointments_bp = Blueprint(
    "appointments",
    __name__
)


def patient_required():

    return "patient_id" in session


def create_notification(
    patient_id,
    title,
    message,
    notification_type="APPOINTMENT",
):

    notification = Notification(
        patient_id=patient_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    db.session.add(notification)


def doctor_available_on_date(
    doctor,
    appointment_date
):

    day = appointment_date.strftime("%a")

    available_days = doctor.available_days or ""

    if "Mon - Sat" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
        ]

    if "Mon - Fri" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
        ]

    if "Mon - Sun" in available_days:
        return True

    return day in available_days


def generate_time_slots(timings):

    if not timings:
        return []

    try:
        start_string, end_string = timings.split(
            " - "
        )

        start_time = datetime.strptime(
            start_string,
            "%I:%M %p"
        )

        end_time = datetime.strptime(
            end_string,
            "%I:%M %p"
        )

    except ValueError:
        return []

    slots = []

    current_time = start_time

    while current_time < end_time:

        slots.append(
            current_time.strftime(
                "%I:%M %p"
            )
        )

        current_time += timedelta(
            minutes=30
        )

    return slots


@appointments_bp.route(
    "/doctor/<int:doctor_id>/book",
    methods=["GET", "POST"]
)
def book_appointment(doctor_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found", 404

    time_slots = generate_time_slots(
        doctor.timings
    )

    if request.method == "POST":

        try:
            appointment_date = datetime.strptime(
                request.form["appointment_date"],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Invalid appointment date.",
            )

        appointment_time = request.form[
            "appointment_time"
        ]

        consultation_type = request.form.get(
            "consultation_type",
            "IN_PERSON"
        )

        if appointment_date < date.today():

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error=(
                    "You cannot book an appointment "
                    "for a past date."
                ),
            )

        if not doctor_available_on_date(
            doctor,
            appointment_date
        ):

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error=(
                    "Doctor is not available "
                    "on this day."
                ),
            )

        if appointment_time not in time_slots:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Invalid appointment time.",
            )

        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor.doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="CONFIRMED",
        ).first()

        if existing_appointment:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error=(
                    "This time slot is already booked."
                ),
            )

        appointment = Appointment(
            patient_id=session["patient_id"],
            doctor_id=doctor.doctor_id,
            hospital_id=doctor.hospital_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            consultation_type=consultation_type,
            status="CONFIRMED",
        )

        db.session.add(appointment)

        create_notification(
            patient_id=session["patient_id"],
            title="Appointment Confirmed",
            message=(
                f"Your appointment with "
                f"{doctor.name} has been confirmed "
                f"for "
                f"{appointment_date.strftime('%d %b %Y')} "
                f"at {appointment_time}."
            ),
        )

        db.session.commit()

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    return render_template(
        "book_appointment.html",
        doctor=doctor,
        time_slots=time_slots,
        today=date.today().isoformat(),
    )


@appointments_bp.route("/appointments")
def my_appointments():

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    today = date.today()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == session["patient_id"],
        Appointment.appointment_date >= today,
        Appointment.status != "CANCELLED",
    ).order_by(
        Appointment.appointment_date.asc()
    ).all()

    past = Appointment.query.filter(
        Appointment.patient_id == session["patient_id"],
        Appointment.appointment_date < today,
    ).order_by(
        Appointment.appointment_date.desc()
    ).all()

    return render_template(
        "appointments.html",
        upcoming=upcoming,
        past=past,
    )


@appointments_bp.route(
    "/appointment/<int:appointment_id>/cancel",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    appointment = db.session.get(
        Appointment,
        appointment_id
    )

    if appointment is None:
        return "Appointment not found", 404

    if (
        appointment.patient_id
        != session["patient_id"]
    ):
        return "Unauthorized", 403

    if appointment.status == "CANCELLED":
        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    appointment.status = "CANCELLED"

    db.session.commit()

    return redirect(
        url_for(
            "appointments.my_appointments"
        )
    )


@appointments_bp.route("/my-doctors")
def my_doctors():

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    patient_id = session["patient_id"]

    doctor_ids = db.session.query(
        Appointment.doctor_id
    ).filter(
        Appointment.patient_id == patient_id
    ).distinct().all()

    doctor_ids = [
        row[0]
        for row in doctor_ids
    ]

    search = request.args.get(
        "q",
        ""
    ).strip()

    if not doctor_ids:

        doctors = []

    else:

        query = Doctor.query.filter(
            Doctor.doctor_id.in_(doctor_ids)
        )

        if search:

            query = query.filter(
                or_(
                    Doctor.name.ilike(
                        f"%{search}%"
                    ),
                    Doctor.specialization.ilike(
                        f"%{search}%"
                    ),
                )
            )

        doctors = query.order_by(
            Doctor.name.asc()
        ).all()

    return render_template(
        "my_doctors.html",
        doctors=doctors,
        search=search,
    )


@appointments_bp.route(
    "/my-doctor/<int:doctor_id>"
)
def doctor_details(doctor_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    previous_appointment = Appointment.query.filter_by(
        patient_id=session["patient_id"],
        doctor_id=doctor_id,
    ).first()

    if previous_appointment is None:
        return (
            "Doctor not found in your "
            "doctors list.",
            404,
        )

    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found.", 404

    return render_template(
        "doctor_details.html",
        doctor=doctor,
    )