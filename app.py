from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime,date,timedelta
from sqlalchemy import or_
import os

app=Flask(__name__)
app.config['SECRET_KEY']='your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "uploads/medical_records"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}
def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )
db = SQLAlchemy(app)

def create_notification(
    patient_id,
    title,
    message,
    notification_type="general"
):

    notification = Notification(

        patient_id=patient_id,

        title=title,

        message=message,

        notification_type=notification_type

    )

    db.session.add(notification)


@app.route('/')
def index():
    return render_template('index.html')

class Patient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False,unique=True)
    password_hash=db.Column(db.String(50),nullable=False)
    phone=db.Column(db.String(15),nullable=False,unique=True)
    date_of_birth=db.Column(db.Date,nullable=False)
    address=db.Column(db.String(100),nullable=True)

class Hospital(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    rating = db.Column(
        db.Float
    )

    review_count = db.Column(
        db.Integer,
        default=0
    )

    image = db.Column(
        db.String(255)
    )

    beds = db.relationship(
        "Bed",
        backref="hospital",
        lazy=True
    )
    doctors = db.relationship(
    "Doctor",
    backref="hospital",
    lazy=True
    )

class Bed(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    bed_type = db.Column(
        db.String(50),
        nullable=False
    )

    total_beds = db.Column(
        db.Integer,
        nullable=False
    )

    available_beds = db.Column(
        db.Integer,
        nullable=False
    )
class Doctor(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    experience = db.Column(
        db.Integer,
        nullable=False
    )

    qualification = db.Column(
        db.String(200)
    )

    consultation_fee = db.Column(
        db.Integer
    )

    available_days = db.Column(
        db.String(100)
    )

    timings = db.Column(
        db.String(100)
    )

    rating = db.Column(
        db.Float,
        default=0
    )

    review_count = db.Column(
        db.Integer,
        default=0
    )

class Appointment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctor.id"),
        nullable=False
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    appointment_date = db.Column(
        db.Date,
        nullable=False
    )

    appointment_time = db.Column(
        db.String(20),
        nullable=False
    )

    consultation_type = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Confirmed",
        nullable=False
    )


    patient = db.relationship(
        "Patient",
        backref="appointments"
    )

    doctor = db.relationship(
        "Doctor",
        backref="appointments"
    )

    hospital = db.relationship(
        "Hospital",
        backref="appointments"
    )

class MedicalRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    filepath = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(50),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    patient = db.relationship(
        "Patient",
        backref="medical_records"
    )

class Notification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    notification_type = db.Column(
        db.String(50),
        nullable=False,
        default="general"
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    patient = db.relationship(
        "Patient",
        backref="notifications"
    )

class Queue(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id"),
        nullable=False,
        unique=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    queue_number = db.Column(
        db.String(20),
        nullable=False
    )

    room = db.Column(
        db.String(50),
        nullable=False,
        default="Room 101"
    )

    position = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Waiting"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    appointment = db.relationship(
        "Appointment",
        backref="queue_entry"
    )

    patient = db.relationship(
        "Patient",
        backref="queue_entries"
    )

    hospital = db.relationship(
        "Hospital",
        backref="queue_entries"
    )

    def get_queue_prefix(department):
        department = department.lower()
        if "dental" in department:
            return "B"
        if "pediatric" in department or "paediatric" in department:
            return "K"
        if "pharmacy" in department:
            return "P"
        return "A"

def get_next_queue_number(department, hospital_id):

    prefix = get_queue_prefix(department)

    today = date.today()

    count = Queue.query.filter(
        Queue.hospital_id == hospital_id,
        Queue.created_at >= datetime.combine(
            today,
            datetime.min.time()
        ),
        Queue.created_at <= datetime.combine(
            today,
            datetime.max.time()
        ),
        Queue.department == department
    ).count()

    return f"{prefix}-{count + 1:03d}"
def create_today_queues():

    today = date.today()

    appointments = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.status == "Confirmed"
    ).order_by(
        Appointment.appointment_time.asc()
    ).all()

    for appointment in appointments:

        # Don't create duplicate queue entries
        existing_queue = Queue.query.filter_by(
            appointment_id=appointment.id
        ).first()

        if existing_queue:
            continue

        department = appointment.doctor.specialization

        # Find current position
        position = Queue.query.filter(
            Queue.hospital_id == appointment.hospital_id,
            Queue.department == department,
            Queue.created_at >= datetime.combine(
                today,
                datetime.min.time()
            ),
            Queue.created_at <= datetime.combine(
                today,
                datetime.max.time()
            )
        ).count() + 1

        queue_number = get_next_queue_number(
            department,
            appointment.hospital_id
        )

        queue = Queue(

            appointment_id=appointment.id,

            patient_id=appointment.patient_id,

            hospital_id=appointment.hospital_id,

            department=department,

            queue_number=queue_number,

            room="Room 101",

            position=position,

            status="Waiting"
        )

        db.session.add(queue)

    db.session.commit()

@app.route("/live-monitor")
def live_monitor():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    create_today_queues()

    return render_template(
        "live_monitor.html"
    )
@app.route("/api/queue")
def get_queue():

    if "patient_id" not in session:
        return {
            "error": "Unauthorized"
        }, 401

    create_today_queues()

    queues = Queue.query.filter(
        Queue.status.in_([
            "Waiting",
            "Calling",
            "Consultation"
        ])
    ).order_by(
        Queue.department.asc(),
        Queue.position.asc()
    ).all()

    result = []

    for queue in queues:

        result.append({

            "id": queue.id,

            "queue_number":
                queue.queue_number,

            "department":
                queue.department,

            "patient_name":
                queue.patient.name,

            "room":
                queue.room,

            "position":
                queue.position,

            "status":
                queue.status
        })

    return result

@app.route(
    "/api/queue/call-next",
    methods=["POST"]
)
def call_next_patient():

    if "patient_id" not in session:
        return {
            "success": False,
            "message": "Unauthorized"
        }, 401

    data = request.get_json()

    department = data.get(
        "department"
    )

    if not department:
        return {
            "success": False,
            "message": "Department is required"
        }, 400

    # Find someone currently being called
    current = Queue.query.filter(
        Queue.department == department,
        Queue.status.in_([
            "Calling",
            "Consultation"
        ])
    ).first()

    if current:

        return {
            "success": False,
            "message":
                f"{current.queue_number} "
                "is still active."
        }, 400

    # Get next waiting patient
    queue = Queue.query.filter(
        Queue.department == department,
        Queue.status == "Waiting"
    ).order_by(
        Queue.position.asc()
    ).first()

    if not queue:

        return {
            "success": False,
            "message": "No patients waiting."
        }, 404

    queue.status = "Calling"

    db.session.commit()

    return {
        "success": True,
        "queue_number":
            queue.queue_number
    }

@app.route(
    "/api/queue/<int:queue_id>/consultation",
    methods=["POST"]
)
def start_consultation(queue_id):

    if "patient_id" not in session:
        return {
            "success": False,
            "message": "Unauthorized"
        }, 401

    queue = db.session.get(
        Queue,
        queue_id
    )

    if queue is None:
        return {
            "success": False,
            "message": "Queue not found"
        }, 404

    queue.status = "Consultation"

    db.session.commit()

    return {
        "success": True
    }

@app.route(
    "/api/queue/<int:queue_id>/complete",
    methods=["POST"]
)
def complete_queue(queue_id):

    if "patient_id" not in session:
        return {
            "success": False,
            "message": "Unauthorized"
        }, 401

    queue = db.session.get(
        Queue,
        queue_id
    )

    if queue is None:
        return {
            "success": False,
            "message": "Queue not found"
        }, 404

    queue.status = "Completed"

    db.session.commit()

    return {
        "success": True
    }
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        phone=request.form['phone']
        date_of_birth = datetime.strptime(
            request.form["date_of_birth"],
            "%Y-%m-%d"
        ).date()
        address=request.form.get('address')

        existing_patient=Patient.query.filter_by(email=email).first()

        if existing_patient:
            return "Email already registered"

        password_hash=generate_password_hash(password)

        new_patient=Patient(name=name,email=email,password_hash=password_hash,phone=phone,date_of_birth=date_of_birth)
        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        patient = Patient.query.filter_by(
            email=email
        ).first()

        if patient and check_password_hash(
            patient.password_hash,
            password
        ):

            session["patient_id"] = patient.id

            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    today = date.today()

    next_appointment = Appointment.query.filter(

        Appointment.patient_id == session["patient_id"],

        Appointment.appointment_date >= date.today(),

        Appointment.status == "Confirmed"

    ).order_by(

        Appointment.appointment_date.asc()

    ).first()

    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == session["patient_id"],
        Appointment.appointment_date >= today,
        Appointment.status == "Confirmed"
    ).count()

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    return render_template(
        "dashboard.html",
        patient=patient,
        next_appointment=next_appointment,
        upcoming_appointments=upcoming_appointments
    )

@app.route("/logout")
def logout():

    session.pop("patient_id", None)

    return redirect(url_for("login"))

@app.route("/hospitals")
def hospitals():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    hospitals = Hospital.query.all()

    return render_template(
        "hospitals.html",
        hospitals=hospitals
    )

@app.route("/hospital/<int:hospital_id>")
def hospital_details(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "hospital_details.html",
        hospital=hospital
    )

@app.route("/hospital/<int:hospital_id>/beds")
def bed_availability(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "beds.html",
        hospital=hospital
    )

@app.route("/hospital/<int:hospital_id>/doctors")
def doctor_list(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

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
        doctors=doctors
    )

@app.route("/doctor/<int:doctor_id>")
def doctor_profile(doctor_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found", 404

    return render_template(
        "doctor_profile.html",
        doctor=doctor
    )

def doctor_available_on_date(doctor, appointment_date):

    day = appointment_date.strftime("%a")

    days = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]

    available_days = doctor.available_days

    if "Mon - Sat" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat"
        ]

    if "Mon - Fri" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri"
        ]

    if "Mon - Sun" in available_days:
        return True

    return day in available_days

def generate_time_slots(timings):

    start_string, end_string = timings.split(" - ")

    start_time = datetime.strptime(
        start_string,
        "%I:%M %p"
    )

    end_time = datetime.strptime(
        end_string,
        "%I:%M %p"
    )


    slots = []

    current_time = start_time


    while current_time < end_time:

        slots.append(
            current_time.strftime("%I:%M %p")
        )

        current_time += timedelta(minutes=30)


    return slots

@app.route(
    "/doctor/<int:doctor_id>/book",
    methods=["GET", "POST"]
)
def book_appointment(doctor_id):

    # Patient must be logged in
    if "patient_id" not in session:
        return redirect(url_for("login"))

    # Find doctor
    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found", 404


    # Generate temporary time slots
    time_slots = generate_time_slots(
        doctor.timings
    )


    # =================================
    # POST - Patient submits booking
    # =================================

    if request.method == "POST":

        # -----------------------------
        # Get form data
        # -----------------------------

        appointment_date = datetime.strptime(
            request.form["appointment_date"],
            "%Y-%m-%d"
        ).date()

        appointment_time = request.form[
            "appointment_time"
        ]

        consultation_type = request.form[
            "consultation_type"
        ]


        # -----------------------------
        # Check past date
        # -----------------------------

        if appointment_date < date.today():

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="You cannot book an appointment for a past date."
            )


        # -----------------------------
        # Check doctor's available day
        # -----------------------------

        if not doctor_available_on_date(
            doctor,
            appointment_date
        ):

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Doctor is not available on this day."
            )


        # -----------------------------
        # Check whether slot is valid
        # -----------------------------

        if appointment_time not in time_slots:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Invalid appointment time."
            )


        # -----------------------------
        # Check duplicate booking
        # -----------------------------

        existing_appointment = Appointment.query.filter_by(

            doctor_id=doctor.id,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            status="Confirmed"

        ).first()


        if existing_appointment:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="This time slot is already booked."
            )


        # -----------------------------
        # Create appointment
        # -----------------------------

        appointment = Appointment(

            patient_id=session["patient_id"],

            doctor_id=doctor.id,

            hospital_id=doctor.hospital_id,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            consultation_type=consultation_type,

            status="Confirmed"
        )


        db.session.add(appointment)
        create_notification(

            patient_id=session["patient_id"],

            title="Appointment Confirmed",

            message=(
                f"Your appointment with "
                f"{doctor.name} has been confirmed "
                f"for {appointment_date.strftime('%d %b %Y')} "
                f"at {appointment_time}."
            ),

            notification_type="appointment"

        )

        db.session.commit()


        # -----------------------------
        # Go to My Appointments
        # -----------------------------

        return redirect(
            url_for("my_appointments")
        )


    # =================================
    # GET - Show booking page
    # =================================

    return render_template(

        "book_appointment.html",

        doctor=doctor,

        time_slots=time_slots,

        today=date.today().isoformat()

    )

@app.route("/appointments")
def my_appointments():

    if "patient_id" not in session:
        return redirect(url_for("login"))


    today = date.today()


    upcoming = Appointment.query.filter(

        Appointment.patient_id == session["patient_id"],

        Appointment.appointment_date >= today,

        Appointment.status != "Cancelled"

    ).order_by(
        Appointment.appointment_date.asc()
    ).all()


    past = Appointment.query.filter(

        Appointment.patient_id == session["patient_id"],

        Appointment.appointment_date < today

    ).order_by(
        Appointment.appointment_date.desc()
    ).all()


    return render_template(
        "appointments.html",
        upcoming=upcoming,
        past=past
    )

@app.route(
    "/appointment/<int:appointment_id>/cancel",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))


    appointment = db.session.get(
        Appointment,
        appointment_id
    )


    if appointment is None:
        return "Appointment not found", 404


    # Make sure this appointment belongs
    # to the logged-in patient

    if appointment.patient_id != session["patient_id"]:

        return "Unauthorized", 403


    # Don't allow cancellation of
    # already cancelled appointment

    if appointment.status == "Cancelled":

        return redirect(
            url_for("my_appointments")
        )


    appointment.status = "Cancelled"


    db.session.commit()


    return redirect(
        url_for("my_appointments")
    )

@app.route("/my-doctors")
def my_doctors():

    # Patient must be logged in
    if "patient_id" not in session:
        return redirect(url_for("login"))

    patient_id = session["patient_id"]


    # ==========================================
    # Find doctors previously booked by patient
    # ==========================================

    doctor_ids = db.session.query(
        Appointment.doctor_id
    ).filter(
        Appointment.patient_id == patient_id
    ).distinct().all()


    # Convert tuples into a simple list of IDs

    doctor_ids = [
        row[0]
        for row in doctor_ids
    ]


    # ==========================================
    # Get search text
    # ==========================================

    search = request.args.get(
        "q",
        ""
    ).strip()


    # ==========================================
    # Find doctors
    # ==========================================

    if doctor_ids:

        query = Doctor.query.filter(
            Doctor.id.in_(doctor_ids)
        )


        # Search by name OR specialization

        if search:

            query = query.filter(
                or_(
                    Doctor.name.ilike(
                        f"%{search}%"
                    ),

                    Doctor.specialization.ilike(
                        f"%{search}%"
                    )
                )
            )


        # Sort alphabetically

        doctors = query.order_by(
            Doctor.name.asc()
        ).all()


    else:

        # Patient has never booked a doctor

        doctors = []


    # ==========================================
    # Send data to template
    # ==========================================

    return render_template(
        "my_doctors.html",
        doctors=doctors,
        search=search
    )

@app.route("/my-doctor/<int:doctor_id>")
def doctor_details(doctor_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))


    # Check that this patient has
    # previously booked this doctor

    previous_appointment = Appointment.query.filter_by(

        patient_id=session["patient_id"],

        doctor_id=doctor_id

    ).first()


    if previous_appointment is None:

        return "Doctor not found in your doctors list.", 404


    doctor = db.session.get(
        Doctor,
        doctor_id
    )


    if doctor is None:
        return "Doctor not found.", 404

    doctor=db.session.get(Doctor,doctor_id)
    if doctor is None:
        return "Doctor not found", 404


    return render_template(
        "doctor_details.html",
        doctor=doctor
    )

@app.route("/medical-records")
def medical_records():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    records = MedicalRecord.query.filter_by(
        patient_id=session["patient_id"]
    ).order_by(
        MedicalRecord.uploaded_at.desc()
    ).all()

    return render_template(
        "medical_records.html",
        records=records
    )

@app.route(
    "/medical-records/upload",
    methods=["GET", "POST"]
)
def upload_medical_record():

    if "patient_id" not in session:
        return redirect(url_for("login"))


    if request.method == "POST":

        file = request.files.get("file")


        # No file selected

        if file is None or file.filename == "":

            return render_template(
                "upload_record.html",
                error="Please select a file."
            )


        # Check extension

        if not allowed_file(file.filename):

            return render_template(
                "upload_record.html",
                error="File type is not allowed."
            )


        # Secure filename

        filename = secure_filename(
            file.filename
        )


        patient_id = session["patient_id"]


        # Create patient's folder

        patient_folder = os.path.join(
            app.config["UPLOAD_FOLDER"],
            str(patient_id)
        )


        os.makedirs(
            patient_folder,
            exist_ok=True
        )


        # Prevent filename conflicts

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        filename = (
            f"{timestamp}_{filename}"
        )


        filepath = os.path.join(
            patient_folder,
            filename
        )


        # Save actual file

        file.save(filepath)


        # Get file information

        file_size = os.path.getsize(
            filepath
        )

        file_type = (
            filename.rsplit(".", 1)[1]
            .lower()
        )


        # Save information in database

        record = MedicalRecord(

            patient_id=patient_id,

            filename=filename,

            filepath=filepath,

            file_type=file_type,

            file_size=file_size

        )


        db.session.add(record)

        db.session.commit()


        return redirect(
            url_for("medical_records")
        )


    return render_template(
        "upload_record.html"
    )

@app.route("/medical-records/<int:record_id>/download")
def download_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # --------------------------------
    # Security check
    # --------------------------------

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    # --------------------------------
    # Get folder and filename
    # --------------------------------

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

@app.route(
    "/medical-records/<int:record_id>/delete",
    methods=["POST"]
)
def delete_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # --------------------------------
    # Security check
    # --------------------------------

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    # --------------------------------
    # Delete physical file
    # --------------------------------

    if os.path.exists(record.filepath):

        os.remove(
            record.filepath
        )

    # --------------------------------
    # Delete database record
    # --------------------------------

    db.session.delete(record)

    db.session.commit()

    return redirect(
        url_for("medical_records")
    )

@app.route("/medical-records/<int:record_id>/analyze")
def analyze_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # Security check
    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    return render_template(
        "medical_report_summary.html",
        record=record
    )

@app.route("/profile")
def profile():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    if patient is None:
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        patient=patient
    )

@app.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
def edit_profile():

    if "patient_id" not in session:
        return redirect(url_for("login"))


    patient = db.session.get(
        Patient,
        session["patient_id"]
    )


    if patient is None:
        return redirect(url_for("login"))


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


        # -----------------------------
        # Basic validation
        # -----------------------------

        if not name:

            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Name is required."
            )


        if not phone:

            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Phone number is required."
            )


        # -----------------------------
        # Date conversion
        # -----------------------------

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
                    error="Invalid date of birth."
                )


        # -----------------------------
        # Update patient
        # -----------------------------

        patient.name = name

        patient.phone = phone

        patient.address = address


        db.session.commit()


        return redirect(
            url_for("profile")
        )


    return render_template(
        "edit_profile.html",
        patient=patient
    )

@app.route("/notifications")
def notifications():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    patient_id = session["patient_id"]

    notifications = Notification.query.filter_by(
        patient_id=patient_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = Notification.query.filter_by(
        patient_id=patient_id,
        is_read=False
    ).count()

    return render_template(
        "notifications.html",
        notifications=notifications,
        unread_count=unread_count
    )

@app.route(
    "/notifications/<int:notification_id>/read",
    methods=["POST"]
)
def mark_notification_read(notification_id):

    if "patient_id" not in session:
        return redirect(url_for("login"))

    notification = db.session.get(
        Notification,
        notification_id
    )

    if notification is None:
        return "Notification not found", 404

    # Security check
    if notification.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    notification.is_read = True

    db.session.commit()

    return redirect(
        url_for("notifications")
    )

@app.context_processor
def inject_notification_count():

    unread_notification_count = 0

    if "patient_id" in session:

        unread_notification_count = Notification.query.filter_by(
            patient_id=session["patient_id"],
            is_read=False
        ).count()

    return {
        "unread_notification_count": unread_notification_count
    }

@app.route(
    "/notifications/read-all",
    methods=["POST"]
)
def mark_all_notifications_read():

    if "patient_id" not in session:
        return redirect(url_for("login"))

    Notification.query.filter_by(
        patient_id=session["patient_id"],
        is_read=False
    ).update(
        {"is_read": True}
    )

    db.session.commit()

    return redirect(
        url_for("notifications")
    )



with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(debug=True)
