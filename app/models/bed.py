from app.extensions import db


class Bed(db.Model):
    __tablename__ = "beds"

    bed_id = db.Column(db.Integer, primary_key=True)

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospitals.hospital_id"),
        nullable=False,
        index=True,
    )

    bed_type = db.Column(db.String(50), nullable=False)
    total_beds = db.Column(db.Integer, nullable=False, default=0)
    available_beds = db.Column(db.Integer, nullable=False, default=0)

    hospital = db.relationship(
        "Hospital",
        back_populates="beds",
    )
