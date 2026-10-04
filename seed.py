from app import create_app
from app.extensions import db
from app.models import Hospital, Bed, Doctor


app = create_app()


def seed_data():
    with app.app_context():

        # -------------------------------------------------
        # Hospitals
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
            hospital = Hospital.query.filter_by(
                name=data["name"]
            ).first()

            if hospital is None:
                hospital = Hospital(**data)
                db.session.add(hospital)
                db.session.flush()

            hospitals[data["name"]] = hospital

        # -------------------------------------------------
        # Beds
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
        # Doctors
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

            existing_doctor = Doctor.query.filter_by(
                hospital_id=hospital.hospital_id,
                name=name
            ).first()

            if existing_doctor is None:
                db.session.add(
                    Doctor(
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
                )

        db.session.commit()

        print("====================================")
        print("HealthForge seed completed")
        print("====================================")
        print("Hospitals:", Hospital.query.count())
        print("Beds:", Bed.query.count())
        print("Doctors:", Doctor.query.count())


if __name__ == "__main__":
    seed_data()