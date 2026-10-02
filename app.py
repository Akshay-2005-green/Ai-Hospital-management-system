from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "healthforge-ai-demo-secret-key-change-me"

# -------------------------------------------------------------------
# Demo data only - no database is used. Everything resets on restart.
# -------------------------------------------------------------------
DOCTOR = {
    "email": "doctor@healthforge.ai",
    "password": "doctor123",
    "name": "Dr. Rahul Verma",
    "specialization": "Cardiologist",
    "qualification": "MBBS, MD (Cardiology)",
    "experience": "10+ Years",
    "phone": "9876543210",
    "photo_initials": "RV",
}

appointments = [
    {"id": 1, "time": "09:00 AM", "patient": "Ramesh Sharma", "age": 45, "gender": "Male",
     "type": "Follow-up", "token": "TK0125", "status": "Checked in"},
    {"id": 2, "time": "10:00 AM", "patient": "Neha Singh", "age": 32, "gender": "Female",
     "type": "Consultation", "token": "TK0126", "status": "Waiting"},
    {"id": 3, "time": "11:30 AM", "patient": "Amit Kumar", "age": 28, "gender": "Male",
     "type": "Consultation", "token": "TK0127", "status": "Waiting"},
    {"id": 4, "time": "02:00 PM", "patient": "Priya Patel", "age": 38, "gender": "Female",
     "type": "Follow-up", "token": "TK0128", "status": "Scheduled"},
    {"id": 5, "time": "03:30 PM", "patient": "Suresh Yadav", "age": 50, "gender": "Male",
     "type": "Consultation", "token": "TK0129", "status": "Scheduled"},
]

patients = [
    {"id": 1, "name": "Ramesh Sharma", "mrn": "HF2500125", "age": 45, "gender": "Male", "last_visit": "10 May 2025"},
    {"id": 2, "name": "Neha Singh", "mrn": "HF2500126", "age": 32, "gender": "Female", "last_visit": "15 May 2025"},
    {"id": 3, "name": "Amit Kumar", "mrn": "HF2500127", "age": 28, "gender": "Male", "last_visit": "15 May 2025"},
    {"id": 4, "name": "Priya Patel", "mrn": "HF2500128", "age": 38, "gender": "Female", "last_visit": "12 May 2025"},
    {"id": 5, "name": "Suresh Yadav", "mrn": "HF2500129", "age": 50, "gender": "Male", "last_visit": "11 May 2025"},
    {"id": 6, "name": "Vikram Joshi", "mrn": "HF2500130", "age": 41, "gender": "Male", "last_visit": "09 May 2025"},
]

schedule = {
    "15 May 2025": [
        {"time": "09:00 AM - 01:00 PM", "enabled": True},
        {"time": "02:00 PM - 05:00 PM", "enabled": True},
        {"time": "05:00 PM - 08:00 PM", "enabled": False},
    ]
}

notifications = [
    {"id": 1, "title": "New appointment booked", "message": "Neha Singh has booked a consultation for today at 10:00 AM.", "time": "10 minutes ago", "type": "appointment", "read": False},
    {"id": 2, "title": "Appointment reminder", "message": "You have 5 appointments scheduled for today.", "time": "30 minutes ago", "type": "reminder", "read": False},
    {"id": 3, "title": "Profile update", "message": "Your profile information was last updated successfully.", "time": "Yesterday", "type": "system", "read": True},
]

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.context_processor
def inject_globals():
    unread = sum(1 for n in notifications if not n["read"])
    return {
        "doctor": DOCTOR,
        "unread_notifications": unread,
        "today": date.today().strftime("%d %b %Y"),
    }

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard") if session.get("logged_in") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if email == DOCTOR["email"] and password == DOCTOR["password"]:
            session["logged_in"] = True
            session["doctor_email"] = email
            flash("Welcome back, Dr. Rahul Verma!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email/phone or password. Use the demo credentials shown below.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    checked_in = sum(1 for a in appointments if a["status"] == "Checked in")
    pending = sum(1 for a in appointments if a["status"] in ("Waiting", "Scheduled"))
    return render_template(
        "dashboard.html",
        appointments=appointments[:5],
        stats={
            "today": len(appointments),
            "seen": checked_in,
            "new_patients": len(patients),
            "pending": pending,
        },
    )

@app.route("/appointments")
@login_required
def appointment_list():
    status = request.args.get("status", "All")
    filtered = appointments if status == "All" else [a for a in appointments if a["status"] == status]
    return render_template("appointments.html", appointments=filtered, current_status=status)

@app.route("/appointments/<int:appointment_id>/status", methods=["POST"])
@login_required
def update_appointment_status(appointment_id):
    new_status = request.form.get("status", "")
    allowed = {"Scheduled", "Waiting", "Checked in", "Completed", "Cancelled"}

    for appointment in appointments:
        if appointment["id"] == appointment_id:
            if new_status in allowed:
                appointment["status"] = new_status
                flash(f"{appointment['patient']}'s appointment is now {new_status}.", "success")
            break

    return redirect(request.referrer or url_for("appointment_list"))

@app.route("/patients")
@login_required
def patient_list():
    query_text = request.args.get("q", "").strip()
    query = query_text.lower()
    gender = request.args.get("gender", "All")

    filtered = patients
    if query:
        filtered = [
            p for p in filtered
            if query in p["name"].lower() or query in p["mrn"].lower()
        ]
    if gender != "All":
        filtered = [p for p in filtered if p["gender"] == gender]

    # Real pagination: the old UI displayed a decorative page 2 button.
    # The page number is now sent to Flask and the correct slice is rendered.
    page_size = 5
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    page = min(page, total_pages)

    start = (page - 1) * page_size
    paginated_patients = filtered[start:start + page_size]

    return render_template(
        "patients.html",
        patients=paginated_patients,
        query=query_text,
        gender=gender,
        page=page,
        total_pages=total_pages,
    )

@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule_page():
    selected_date = request.values.get("date", "15 May 2025")

    if selected_date not in schedule:
        schedule[selected_date] = []

    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle":
            index = int(request.form.get("index", -1))
            if 0 <= index < len(schedule[selected_date]):
                schedule[selected_date][index]["enabled"] = not schedule[selected_date][index]["enabled"]
                flash("Schedule availability updated.", "success")

        elif action == "add":
            start = request.form.get("start", "").strip()
            end = request.form.get("end", "").strip()
            if start and end:
                schedule[selected_date].append({
                    "time": f"{start} - {end}",
                    "enabled": True
                })
                flash("New time slot added.", "success")
            else:
                flash("Please enter both start and end times.", "error")

        elif action == "save":
            flash("Schedule saved successfully.", "success")

        return redirect(url_for("schedule_page", date=selected_date))

    return render_template(
        "schedule.html",
        selected_date=selected_date,
        slots=schedule[selected_date],
    )

@app.route("/notifications")
@login_required
def notification_page():
    return render_template("notifications.html", notifications=notifications)

@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    for notification in notifications:
        if notification["id"] == notification_id:
            notification["read"] = True
            break
    return redirect(url_for("notification_page"))

@app.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():
    for notification in notifications:
        notification["read"] = True
    flash("All notifications marked as read.", "success")
    return redirect(url_for("notification_page"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        DOCTOR["name"] = request.form.get("name", DOCTOR["name"]).strip() or DOCTOR["name"]
        DOCTOR["email"] = request.form.get("email", DOCTOR["email"]).strip() or DOCTOR["email"]
        DOCTOR["phone"] = request.form.get("phone", DOCTOR["phone"]).strip() or DOCTOR["phone"]
        DOCTOR["specialization"] = request.form.get("specialization", DOCTOR["specialization"]).strip() or DOCTOR["specialization"]
        DOCTOR["qualification"] = request.form.get("qualification", DOCTOR["qualification"]).strip() or DOCTOR["qualification"]
        DOCTOR["experience"] = request.form.get("experience", DOCTOR["experience"]).strip() or DOCTOR["experience"]
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html")

# Simple JSON endpoints for future frontend integrations.
@app.route("/api/appointments")
@login_required
def api_appointments():
    return jsonify(appointments)

@app.route("/api/patients")
@login_required
def api_patients():
    return jsonify(patients)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
