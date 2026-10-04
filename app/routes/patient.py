import os

from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
)

from werkzeug.utils import secure_filename

from app.extensions import db

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.notification import Notification


patient_bp = Blueprint("patient", __name__)


ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
}


def login_required():
    return "patient_id" in session


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@patient_bp.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    today = date.today()

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    if patient is None:
        session.clear()
        return redirect(
            url_for("auth.login")
        )

    next_appointment = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.appointment_date >= today,
        Appointment.status == "CONFIRMED",
    ).order_by(
        Appointment.appointment_date.asc()
    ).first()

    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.appointment_date >= today,
        Appointment.status == "CONFIRMED",
    ).count()

    return render_template(
        "dashboard.html",
        patient=patient,
        next_appointment=next_appointment,
        upcoming_appointments=upcoming_appointments,
    )


@patient_bp.route("/profile")
def profile():

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    if patient is None:
        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "profile.html",
        patient=patient,
    )


@patient_bp.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
def edit_profile():

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    if patient is None:
        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        if not name:
            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Name is required.",
            )

        if not phone:
            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Phone number is required.",
            )

        if date_of_birth:

            try:

                patient.date_of_birth = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return render_template(
                    "edit_profile.html",
                    patient=patient,
                    error="Invalid date of birth.",
                )

        patient.name = name
        patient.phone = phone
        patient.address = address

        db.session.commit()

        return redirect(
            url_for("patient.profile")
        )

    return render_template(
        "edit_profile.html",
        patient=patient,
    )


@patient_bp.route("/medical-records")
def medical_records():

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    records = MedicalRecord.query.filter_by(
        patient_id=session["patient_id"]
    ).order_by(
        MedicalRecord.uploaded_at.desc()
    ).all()

    return render_template(
        "medical_records.html",
        records=records,
    )


@patient_bp.route(
    "/medical-records/upload",
    methods=["GET", "POST"]
)
def upload_medical_record():

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        file = request.files.get("file")

        if file is None or file.filename == "":
            return render_template(
                "upload_record.html",
                error="Please select a file.",
            )

        if not allowed_file(file.filename):
            return render_template(
                "upload_record.html",
                error="File type is not allowed.",
            )

        filename = secure_filename(
            file.filename
        )

        patient_id = session["patient_id"]

        upload_folder = os.path.join(
            "uploads",
            "medical_records",
            str(patient_id)
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        filename = (
            f"{timestamp}_{filename}"
        )

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)

        file_size = os.path.getsize(
            filepath
        )

        file_type = (
            filename.rsplit(".", 1)[1]
            .lower()
        )

        record = MedicalRecord(
            patient_id=patient_id,
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            file_size=file_size,
        )

        db.session.add(record)
        db.session.commit()

        return redirect(
            url_for("patient.medical_records")
        )

    return render_template(
        "upload_record.html"
    )


@patient_bp.route(
    "/medical-records/<int:record_id>/download"
)
def download_medical_record(record_id):

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    directory = os.path.dirname(
        record.filepath
    )

    filename = os.path.basename(
        record.filepath
    )

    return send_from_directory(
        directory,
        filename,
        as_attachment=True
    )


@patient_bp.route(
    "/medical-records/<int:record_id>/delete",
    methods=["POST"]
)
def delete_medical_record(record_id):

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    if os.path.exists(record.filepath):
        os.remove(record.filepath)

    db.session.delete(record)
    db.session.commit()

    return redirect(
        url_for("patient.medical_records")
    )


@patient_bp.route(
    "/medical-records/<int:record_id>/analyze"
)
def analyze_medical_record(record_id):

    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    return render_template(
        "medical_report_summary.html",
        record=record,
    )