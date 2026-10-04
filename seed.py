from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import (
    Hospital,
    Bed,
    Doctor,
    Patient,
    Appointment,
    QueueEntry,
    MedicalRecord,
    Notification,
)


app = create_app()


def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # -------------------------------------------------
        # 1. Hospitals
        # -------------------------------------------------
        hospitals_data = [
            {
                "name": "City Care Hospital",
                "location": "Lucknow",
                "description": "Multi-specialty hospital with emergency and critical care services.",
                "rating": 4.7,
                "review_count": 820,
            },
            {
                "name": "MediLife Hospital",
                "location": "Lucknow",
                "description": "Modern hospital providing specialized medical services.",
                "rating": 4.6,
                "review_count": 710,
            },
            {
                "name": "Sunrise Hospital",
                "location": "Lucknow",
                "description": "Hospital providing general and orthopedic healthcare services.",
                "rating": 4.4,
                "review_count": 430,
            },
        ]

        hospitals = {}
        for data in hospitals_data:
            hospital = Hospital.query.filter_by(name=data["name"]).first()
            if hospital is None:
                hospital = Hospital(**data)
                db.session.add(hospital)
                db.session.flush()
            hospitals[data["name"]] = hospital

        # -------------------------------------------------
        # 2. Beds
        # -------------------------------------------------
        bed_data = [
            ("City Care Hospital", "General Beds", 100, 25),
            ("City Care Hospital", "ICU Beds", 20, 5),
            ("City Care Hospital", "Private Rooms", 15, 8),
            ("City Care Hospital", "Ventilator", 10, 2),

            ("MediLife Hospital", "General Beds", 80, 12),
            ("MediLife Hospital", "ICU Beds", 15, 4),

            ("Sunrise Hospital", "General Beds", 70, 18),
            ("Sunrise Hospital", "ICU Beds", 12, 3),
        ]

        for hospital_name, bed_type, total, available in bed_data:
            hospital = hospitals[hospital_name]
            existing_bed = Bed.query.filter_by(
                hospital_id=hospital.hospital_id,
                bed_type=bed_type
            ).first()

            if existing_bed is None:
                db.session.add(
                    Bed(
                        hospital_id=hospital.hospital_id,
                        bed_type=bed_type,
                        total_beds=total,
                        available_beds=available,
                    )
                )

        # -------------------------------------------------
        # 3. Doctors
        # -------------------------------------------------
        doctors_data = [
            (
                "City Care Hospital",
                "Dr. Rahul Verma",
                "Cardiologist",
                10,
                "MBBS, MD (Medicine), DM (Cardiology)",
                800,
                "Mon - Sat",
                "10:00 AM - 05:00 PM",
                4.7,
                820,
            ),
            (
                "City Care Hospital",
                "Dr. Neha Singh",
                "Neurologist",
                8,
                "MBBS, MD, DM (Neurology)",
                700,
                "Mon - Fri",
                "09:00 AM - 03:00 PM",
                4.6,
                650,
            ),
            (
                "City Care Hospital",
                "Dr. Amit Kumar",
                "Orthopedic",
                12,
                "MBBS, MS (Orthopedics)",
                600,
                "Mon - Sat",
                "11:00 AM - 04:00 PM",
                4.5,
                720,
            ),
            (
                "City Care Hospital",
                "Dr. Priya Sharma",
                "Gynecologist",
                9,
                "MBBS, MD (Gynecology)",
                700,
                "Mon - Fri",
                "10:00 AM - 02:00 PM",
                4.8,
                590,
            ),
            (
                "MediLife Hospital",
                "Dr. Arjun Mehta",
                "Cardiologist",
                11,
                "MBBS, MD, DM",
                900,
                "Mon - Sat",
                "10:00 AM - 04:00 PM",
                4.6,
                710,
            ),
            (
                "Sunrise Hospital",
                "Dr. Rohan Gupta",
                "Orthopedic",
                7,
                "MBBS, MS",
                600,
                "Mon - Fri",
                "09:00 AM - 02:00 PM",
                4.4,
                430,
            ),
        ]

        doctors = {}
        for (
            hospital_name,
            name,
            specialization,
            experience,
            qualification,
            consultation_fee,
            available_days,
            timings,
            rating,
            review_count,
        ) in doctors_data:
            hospital = hospitals[hospital_name]
            doctor = Doctor.query.filter_by(
                hospital_id=hospital.hospital_id,
                name=name
            ).first()

            if doctor is None:
                doctor = Doctor(
                    hospital_id=hospital.hospital_id,
                    name=name,
                    specialization=specialization,
                    experience=experience,
                    qualification=qualification,
                    consultation_fee=consultation_fee,
                    available_days=available_days,
                    timings=timings,
                    rating=rating,
                    review_count=review_count,
                )
                db.session.add(doctor)
                db.session.flush()
            doctors[name] = doctor

        # -------------------------------------------------
        # 4. Patients
        # -------------------------------------------------
        patients_data = [
            {
                "name": "Dr. Rahul Verma",
                "email": "doctor@healthforge.ai",
                "password": "doctor123",
                "phone": "9876543210",
                "dob": date(1985, 1, 1),
                "address": "HealthForge Clinic, Lucknow",
            },
            {
                "name": "Rajesh Kumar",
                "email": "patient@healthforge.ai",
                "password": "patient123",
                "phone": "9876500001",
                "dob": date(1988, 5, 14),
                "address": "Hazratganj, Lucknow",
            },
            {
                "name": "Aarav Sharma",
                "email": "aarav.sharma@example.com",
                "password": "password123",
                "phone": "9876500002",
                "dob": date(1992, 8, 22),
                "address": "Gomti Nagar, Lucknow",
            },
            {
                "name": "Ananya Singh",
                "email": "ananya.singh@example.com",
                "password": "password123",
                "phone": "9876500003",
                "dob": date(1995, 12, 10),
                "address": "Aliganj, Lucknow",
            },
            {
                "name": "Vikram Joshi",
                "email": "vikram.joshi@example.com",
                "password": "password123",
                "phone": "9876500004",
                "dob": date(1985, 3, 30),
                "address": "Indira Nagar, Lucknow",
            },
        ]

        patients = {}
        for pdata in patients_data:
            patient = Patient.query.filter_by(email=pdata["email"]).first()
            if patient is None:
                patient = Patient(
                    name=pdata["name"],
                    email=pdata["email"],
                    password_hash=generate_password_hash(pdata["password"]),
                    phone=pdata["phone"],
                    date_of_birth=pdata["dob"],
                    address=pdata["address"],
                )
                db.session.add(patient)
                db.session.flush()
            patients[pdata["email"]] = patient

        # -------------------------------------------------
        # 5. Appointments & Queue Entries
        # -------------------------------------------------
        sample_appointments = [
            {
                "patient": patients["doctor@healthforge.ai"],
                "doctor": doctors["Dr. Rahul Verma"],
                "hospital": hospitals["City Care Hospital"],
                "date": date.today(),
                "time": "10:30 AM",
                "status": "CONFIRMED",
                "type": "IN_PERSON",
                "reason": "Routine Cardiology Consultation and ECG checkup",
                "queue_num": "Q-101",
                "dept": "Cardiology",
                "room": "OPD Room 102",
                "queue_status": "WAITING",
                "pos": 1,
            },
            {
                "patient": patients["doctor@healthforge.ai"],
                "doctor": doctors["Dr. Rahul Verma"],
                "hospital": hospitals["City Care Hospital"],
                "date": date.today(),
                "time": "11:00 AM",
                "status": "CHECKED_IN",
                "type": "IN_PERSON",
                "reason": "Frequent migraine and nerve assessment",
                "queue_num": "Q-102",
                "dept": "Neurology",
                "room": "OPD Room 204",
                "queue_status": "CALLED",
                "pos": 2,
            },
            {
                "patient": patients["ananya.singh@example.com"],
                "doctor": doctors["Dr. Amit Kumar"],
                "hospital": hospitals["City Care Hospital"],
                "date": date.today() + timedelta(days=2),
                "time": "02:00 PM",
                "status": "SCHEDULED",
                "type": "IN_PERSON",
                "reason": "Knee joint inflammation and physical checkup",
                "queue_num": None,
                "dept": None,
                "room": None,
                "queue_status": None,
                "pos": None,
            },
            {
                "patient": patients["patient@healthforge.ai"],
                "doctor": doctors["Dr. Priya Sharma"],
                "hospital": hospitals["City Care Hospital"],
                "date": date.today() - timedelta(days=5),
                "time": "11:30 AM",
                "status": "COMPLETED",
                "type": "IN_PERSON",
                "reason": "Annual preventative wellness screening",
                "queue_num": None,
                "dept": None,
                "room": None,
                "queue_status": None,
                "pos": None,
            },
        ]

        for appt_info in sample_appointments:
            appt = Appointment.query.filter_by(
                patient_id=appt_info["patient"].patient_id,
                doctor_id=appt_info["doctor"].doctor_id,
                appointment_date=appt_info["date"],
                appointment_time=appt_info["time"],
            ).first()

            if appt is None:
                appt = Appointment(
                    patient_id=appt_info["patient"].patient_id,
                    doctor_id=appt_info["doctor"].doctor_id,
                    hospital_id=appt_info["hospital"].hospital_id,
                    appointment_date=appt_info["date"],
                    appointment_time=appt_info["time"],
                    status=appt_info["status"],
                    consultation_type=appt_info["type"],
                    reason=appt_info["reason"],
                )
                db.session.add(appt)
                db.session.flush()

                if appt_info["queue_num"]:
                    qentry = QueueEntry.query.filter_by(appointment_id=appt.appointment_id).first()
                    if qentry is None:
                        qentry = QueueEntry(
                            appointment=appt,
                            patient=appt_info["patient"],
                            doctor=appt_info["doctor"],
                            hospital=appt_info["hospital"],
                            department=appt_info["dept"],
                            queue_number=appt_info["queue_num"],
                            room=appt_info["room"],
                            position=appt_info["pos"],
                            status=appt_info["queue_status"],
                        )
                        db.session.add(qentry)

        # -------------------------------------------------
        # 6. Medical Records
        # -------------------------------------------------
        sample_records = [
            {
                "patient": patients["patient@healthforge.ai"],
                "doctor": doctors["Dr. Rahul Verma"],
                "filename": "ECG_Diagnostic_Report.pdf",
                "filepath": "uploads/ecg_report_01.pdf",
                "file_type": "PDF",
                "file_size": 245000,
                "diagnosis": "Normal Sinus Rhythm. Mild Sinus Tachycardia on exertion.",
                "notes": "Patient advised 30 min daily brisk walking and follow-up after 3 months.",
            },
            {
                "patient": patients["patient@healthforge.ai"],
                "doctor": doctors["Dr. Neha Singh"],
                "filename": "Brain_MRI_Screening.pdf",
                "filepath": "uploads/mri_scan_02.pdf",
                "file_type": "PDF",
                "file_size": 1820000,
                "diagnosis": "No acute intracranial pathology. Mild tension headache.",
                "notes": "Recommended hydration and stress management.",
            },
        ]

        for rec in sample_records:
            existing_rec = MedicalRecord.query.filter_by(
                patient_id=rec["patient"].patient_id,
                filename=rec["filename"],
            ).first()
            if existing_rec is None:
                db.session.add(
                    MedicalRecord(
                        patient_id=rec["patient"].patient_id,
                        doctor_id=rec["doctor"].doctor_id,
                        filename=rec["filename"],
                        filepath=rec["filepath"],
                        file_type=rec["file_type"],
                        file_size=rec["file_size"],
                        diagnosis=rec["diagnosis"],
                        notes=rec["notes"],
                    )
                )

        # -------------------------------------------------
        # 7. Notifications
        # -------------------------------------------------
        sample_notifications = [
            {
                "patient": patients["patient@healthforge.ai"],
                "title": "Queue Token Assigned",
                "message": "Your queue token #Q-101 has been assigned for Dr. Rahul Verma at City Care Hospital.",
                "type": "QUEUE",
                "is_read": False,
            },
            {
                "patient": patients["patient@healthforge.ai"],
                "title": "Lab Report Ready",
                "message": "Your ECG Diagnostic Report is now available in your Medical Records vault.",
                "type": "MEDICAL_RECORD",
                "is_read": True,
            },
            {
                "patient": patients["patient@healthforge.ai"],
                "title": "Appointment Reminder",
                "message": "Upcoming appointment with Dr. Rahul Verma on " + date.today().strftime("%d %b %Y") + " at 10:30 AM.",
                "type": "APPOINTMENT",
                "is_read": False,
            },
        ]

        for notif in sample_notifications:
            existing_notif = Notification.query.filter_by(
                patient_id=notif["patient"].patient_id,
                title=notif["title"],
            ).first()
            if existing_notif is None:
                db.session.add(
                    Notification(
                        patient_id=notif["patient"].patient_id,
                        title=notif["title"],
                        message=notif["message"],
                        notification_type=notif["type"],
                        is_read=notif["is_read"],
                    )
                )

        db.session.commit()

        print("====================================")
        print("HealthForge Sample Data Seeded!")
        print("====================================")
        print("Hospitals:", Hospital.query.count())
        print("Beds:", Bed.query.count())
        print("Doctors:", Doctor.query.count())
        print("Patients:", Patient.query.count())
        print("Appointments:", Appointment.query.count())
        print("Queue Entries:", QueueEntry.query.count())
        print("Medical Records:", MedicalRecord.query.count())
        print("Notifications:", Notification.query.count())


if __name__ == "__main__":
    seed_data()