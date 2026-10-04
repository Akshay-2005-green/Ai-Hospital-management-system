from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app.extensions import db
from app.models.patient import Patient


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        phone = request.form["phone"].strip()

        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address", "").strip()

        existing_patient = Patient.query.filter_by(
            email=email
        ).first()

        if existing_patient:
            return "Email already registered"

        existing_phone = Patient.query.filter_by(
            phone=phone
        ).first()

        if existing_phone:
            return "Phone number already registered"

        dob = None

        if date_of_birth:
            try:
                dob = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                return "Invalid date of birth"

        patient = Patient(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            date_of_birth=dob,
            address=address,
        )

        db.session.add(patient)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]
        selected_role = (request.form.get("role") or "patient").strip().lower()

        if selected_role == "doctor" and email == "doctor@healthforge.ai" and password == "doctor123":
            session.clear()
            session["role"] = "doctor"
            session["doctor_id"] = 1
            session["doctor_name"] = "Dr. Rahul Verma"
            return redirect(url_for("doctor.dashboard"))

        if selected_role == "receptionist" and email == "receptionist@healthforge.ai" and password == "receptionist123":
            session.clear()
            session["role"] = "receptionist"
            session["receptionist_id"] = 1
            session["receptionist_name"] = "Reception Desk"
            return redirect(url_for("receptionist.dashboard"))

        patient = Patient.query.filter_by(
            email=email
        ).first()

        if patient is None and email == "doctor@healthforge.ai" and password == "doctor123":
            patient = Patient(
                name="Dr. Rahul Verma",
                email=email,
                password_hash=generate_password_hash(password),
                phone="9876543210",
                address="HealthForge Clinic, Lucknow",
            )
            db.session.add(patient)
            db.session.commit()

        if patient and check_password_hash(
            patient.password_hash,
            password
        ):
            session.clear()
            session["role"] = "patient"
            session["patient_id"] = patient.patient_id
            return redirect(
                url_for("patient.dashboard")
            )

        return "Invalid email or password"

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("auth.login")
    )