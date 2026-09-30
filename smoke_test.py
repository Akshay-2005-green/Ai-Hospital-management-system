"""Basic local smoke test for HealthForge AI.

Run after installing requirements:
    python smoke_test.py
"""
from app import app


def check(client, method, path, expected_status=200, data=None, follow_redirects=False):
    response = getattr(client, method)(path, data=data, follow_redirects=follow_redirects)
    assert response.status_code == expected_status, f"{method.upper()} {path}: expected {expected_status}, got {response.status_code}"
    return response


with app.test_client() as client:
    # Public login page.
    check(client, "get", "/login")

    # Protected pages must redirect when logged out.
    for path in ["/dashboard", "/appointments", "/patients", "/schedule", "/notifications", "/profile"]:
        check(client, "get", path, expected_status=302)

    # Login and render every protected page.
    response = check(
        client,
        "post",
        "/login",
        data={"email": "doctor@healthforge.ai", "password": "doctor123"},
        expected_status=302,
    )
    assert "/dashboard" in response.headers["Location"]

    for path in ["/dashboard", "/appointments", "/patients", "/schedule", "/notifications", "/profile"]:
        response = check(client, "get", path)
        assert b"HealthForge" in response.data, f"{path} did not render expected page content"

    # Requested UI cleanup checks.
    dashboard_html = check(client, "get", "/dashboard").data.decode("utf-8")
    patients_html = check(client, "get", "/patients").data.decode("utf-8")
    login_html = check(client, "get", "/login").data.decode("utf-8") if False else ""
    assert "Here is what's happening with your practice today." not in dashboard_html
    assert "Search and manage the patients assigned to your practice." not in patients_html
    assert "timeline-row-button" in dashboard_html
    assert "/appointments/1/status" in dashboard_html

    # Patient page 2 must be a real Flask page, not a decorative button.
    page2 = check(client, "get", "/patients?page=2").data.decode("utf-8")
    assert "Vikram Joshi" in page2
    assert 'class="pagination-button current" href="/patients?page=2' in page2

    # Exercise representative POST actions.
    check(client, "post", "/appointments/2/status", expected_status=302, data={"status": "Checked in"})
    check(client, "post", "/schedule", expected_status=302, data={
        "action": "add", "date": "15 May 2025", "start": "09:00 AM", "end": "10:00 AM"
    })
    check(client, "post", "/notifications/1/read", expected_status=302)
    check(client, "post", "/notifications/read-all", expected_status=302)
    check(client, "post", "/profile", expected_status=302, data={
        "name": "Dr. Rahul Verma", "email": "doctor@healthforge.ai", "phone": "9876543210",
        "specialization": "Cardiologist", "qualification": "MBBS, MD (Cardiology)", "experience": "10+ Years"
    })

print("Smoke test passed: login, protected pages, templates, and representative actions are working.")
