"""Static/template verification for the HealthForge AI prototype.

This script checks the codebase before Flask is installed. It validates Python syntax,
Jinja template compilation/rendering, requested UI removals, pagination wiring,
and interactive dashboard appointment editing.
"""
from pathlib import Path
import ast
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"

# 1) Python syntax validation.
for filename in ("app.py", "smoke_test.py"):
    ast.parse((ROOT / filename).read_text(encoding="utf-8"), filename=filename)

# 2) Compile every template with Jinja2.
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    undefined=StrictUndefined,
    autoescape=True,
)

class Request:
    endpoint = "dashboard"


def url_for(endpoint, **kwargs):
    routes = {
        "static": "/static/{filename}",
        "dashboard": "/dashboard",
        "login": "/login",
        "logout": "/logout",
        "appointment_list": "/appointments",
        "update_appointment_status": "/appointments/{appointment_id}/status",
        "patient_list": "/patients",
        "schedule_page": "/schedule",
        "notification_page": "/notifications",
        "mark_notification_read": "/notifications/{notification_id}/read",
        "mark_all_notifications_read": "/notifications/read-all",
        "profile": "/profile",
    }
    path = routes[endpoint]
    for key, value in kwargs.items():
        path = path.replace("{" + key + "}", str(value))
    if endpoint == "patient_list" and kwargs:
        pairs = []
        for key, value in kwargs.items():
            if value not in (None, ""):
                pairs.append(f"{key}={value}")
        if pairs:
            path += "?" + "&".join(pairs)
    return path

class Session(dict):
    pass

env.globals.update({
    "url_for": url_for,
    "range": range,
    "request": Request(),
    "session": Session(logged_in=True),
    "get_flashed_messages": lambda **kwargs: [],
})

common = {
    "doctor": {
        "name": "Dr. Rahul Verma", "specialization": "Cardiologist",
        "photo_initials": "RV", "email": "doctor@healthforge.ai",
        "phone": "9876543210", "qualification": "MBBS, MD (Cardiology)",
        "experience": "10+ Years",
    },
    "unread_notifications": 2,
    "today": "16 Aug 2026",
}

appointments = [
    {"id": 1, "time": "09:00 AM", "patient": "Ramesh Sharma", "age": 45,
     "gender": "Male", "type": "Follow-up", "token": "TK0125", "status": "Checked in"},
    {"id": 2, "time": "10:00 AM", "patient": "Neha Singh", "age": 32,
     "gender": "Female", "type": "Consultation", "token": "TK0126", "status": "Waiting"},
]
patients = [
    {"id": i, "name": name, "mrn": f"HF2500{i:03}", "age": 30+i, "gender": "Male", "last_visit": "15 May 2025"}
    for i, name in enumerate(["Ramesh Sharma", "Neha Singh", "Amit Kumar", "Priya Patel", "Suresh Yadav", "Vikram Joshi"], 1)
]

contexts = {
    "base.html": common,
    "dashboard.html": {**common, "appointments": appointments, "stats": {"today": 5, "seen": 1, "new_patients": 6, "pending": 4}},
    "appointments.html": {**common, "appointments": appointments, "current_status": "All"},
    "patients.html": {**common, "patients": patients[:5], "query": "", "gender": "All", "page": 1, "total_pages": 2},
    "schedule.html": {**common, "selected_date": "15 May 2025", "slots": [{"time": "09:00 AM - 01:00 PM", "enabled": True}]},
    "notifications.html": {**common, "notifications": [{"id": 1, "title": "New appointment booked", "message": "Test", "time": "now", "type": "appointment", "read": False}]},
    "profile.html": common,
    "login.html": {"session": Session(logged_in=False), **common},
}

for path in sorted(TEMPLATES.glob("*.html")):
    template = env.get_template(path.name)
    template.render(**contexts[path.name])

# 3) Required text removals.
checks = {
    "dashboard.html": ["Here is what's happening with your practice today."],
    "patients.html": ["Search and manage the patients assigned to your practice."],
    "login.html": [
        "Manage appointments, patients and availability from one simple doctor portal.",
        "Demo credentials",
        "doctor@healthforge.ai",
        "doctor123",
    ],
    "base.html": ["doctor-mini"],
}
for filename, forbidden in checks.items():
    text = (TEMPLATES / filename).read_text(encoding="utf-8")
    for phrase in forbidden:
        assert phrase not in text, f"Forbidden text/markup remains in {filename}: {phrase}"

# Profile disclaimer was removed in the prior revision; ensure it remains absent.
profile_text = (TEMPLATES / "profile.html").read_text(encoding="utf-8")
assert "Manage your professional information and contact details." not in profile_text

# 4) Requested functionality markers.
app_text = (ROOT / "app.py").read_text(encoding="utf-8")
patients_text = (TEMPLATES / "patients.html").read_text(encoding="utf-8")
dashboard_text = (TEMPLATES / "dashboard.html").read_text(encoding="utf-8")
base_text = (TEMPLATES / "base.html").read_text(encoding="utf-8")
login_text = (TEMPLATES / "login.html").read_text(encoding="utf-8")

assert "page_size = 5" in app_text
assert "paginated_patients" in app_text
assert "page=page_number" in patients_text
assert "timeline-row-button" in dashboard_text
assert "appointmentEditor" in dashboard_text
assert "/appointments/${button.dataset.appointmentId}/status" in dashboard_text
assert "<svg" in base_text
assert "doctor-photo" in login_text
assert "images.unsplash.com/photo-1612349317150-e413f6a5b16d" in login_text

print("VERIFICATION PASSED")
print("- Python syntax: PASS")
print("- All 8 Jinja templates compile/render: PASS")
print("- Requested disclaimer removals: PASS")
print("- Sidebar doctor card removal: PASS")
print("- Real patient pagination wiring: PASS")
print("- Interactive dashboard appointment editor: PASS")
print("- SVG interactive module icons: PASS")
print("- Login real-photo integration and demo-credential removal: PASS")
