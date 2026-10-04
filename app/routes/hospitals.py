from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)

from app.extensions import db

from app.models.hospital import Hospital
from app.models.doctor import Doctor


hospitals_bp = Blueprint(
    "hospitals",
    __name__
)


def patient_required():

    return "patient_id" in session


@hospitals_bp.route("/hospitals")
def hospitals():

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    hospitals = Hospital.query.all()

    return render_template(
        "hospitals.html",
        hospitals=hospitals,
    )


@hospitals_bp.route(
    "/hospital/<int:hospital_id>"
)
def hospital_details(hospital_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "hospital_details.html",
        hospital=hospital,
    )


@hospitals_bp.route(
    "/hospital/<int:hospital_id>/beds"
)
def bed_availability(hospital_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "beds.html",
        hospital=hospital,
    )


@hospitals_bp.route(
    "/hospital/<int:hospital_id>/doctors"
)
def doctor_list(hospital_id):

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    doctors = Doctor.query.filter_by(
        hospital_id=hospital_id
    ).all()

    return render_template(
        "doctors.html",
        hospital=hospital,
        doctors=doctors,
    )


@hospitals_bp.route(
    "/doctor/<int:doctor_id>"
)
def doctor_profile(doctor_id):

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

    return render_template(
        "doctor_profile.html",
        doctor=doctor,
    )