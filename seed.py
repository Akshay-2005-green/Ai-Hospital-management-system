from datetime import date
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.database import User, DoctorProfile, Bed, Appointment

app, socketio = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    users = [
        User(name="Akshay Sachan", email="patient@healthforge.ai", password=generate_password_hash("123456"), role="patient"),
        User(name="Dr. Rahul Verma", email="doctor@healthforge.ai", password=generate_password_hash("123456"), role="doctor"),
        User(name="Receptionist", email="reception@healthforge.ai", password=generate_password_hash("123456"), role="receptionist"),
        User(name="Hospital Admin", email="admin@healthforge.ai", password=generate_password_hash("123456"), role="admin"),
    ]
    db.session.add_all(users)
    db.session.commit()

    doctor = users[1]
    db.session.add(DoctorProfile(
        user_id=doctor.id, specialization="Cardiology",
        qualification="MBBS, MD (Cardiology)", experience=10,
        consultation_minutes=12, available=True
    ))

    db.session.add_all([
        Bed(ward="General Ward", total=60, available=18),
        Bed(ward="Private Room", total=30, available=6),
        Bed(ward="ICU", total=15, available=3),
        Bed(ward="Emergency", total=15, available=2),
    ])

    db.session.commit()
    print("Seed complete.")
    print("Patient: patient@healthforge.ai / 123456")
    print("Doctor: doctor@healthforge.ai / 123456")
    print("Receptionist: reception@healthforge.ai / 123456")
    print("Admin: admin@healthforge.ai / 123456")
