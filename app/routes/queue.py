from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
)

from app.extensions import db

from app.models.appointment import Appointment
from app.models.queue_entry import QueueEntry


queue_bp = Blueprint(
    "queue",
    __name__
)


def patient_required():

    return "patient_id" in session


def get_queue_prefix(department):

    department = department.lower()

    if "dental" in department:
        return "B"

    if (
        "pediatric" in department
        or "paediatric" in department
    ):
        return "K"

    if "pharmacy" in department:
        return "P"

    return "A"


def get_next_queue_number(
    department,
    hospital_id
):

    prefix = get_queue_prefix(
        department
    )

    today = date.today()

    count = QueueEntry.query.filter(
        QueueEntry.hospital_id == hospital_id,
        QueueEntry.department == department,
        QueueEntry.joined_at >= datetime.combine(
            today,
            datetime.min.time()
        ),
        QueueEntry.joined_at <= datetime.combine(
            today,
            datetime.max.time()
        ),
    ).count()

    return f"{prefix}-{count + 1:03d}"


def create_today_queues():

    today = date.today()

    appointments = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.status == "CONFIRMED",
    ).order_by(
        Appointment.appointment_time.asc()
    ).all()

    for appointment in appointments:

        existing_queue = QueueEntry.query.filter_by(
            appointment_id=appointment.appointment_id
        ).first()

        if existing_queue:
            continue

        department = (
            appointment.doctor.specialization
        )

        position = QueueEntry.query.filter(
            QueueEntry.hospital_id
            == appointment.hospital_id,

            QueueEntry.department
            == department,

            QueueEntry.joined_at >= datetime.combine(
                today,
                datetime.min.time()
            ),

            QueueEntry.joined_at <= datetime.combine(
                today,
                datetime.max.time()
            ),
        ).count() + 1

        queue_number = get_next_queue_number(
            department,
            appointment.hospital_id
        )

        queue = QueueEntry(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            hospital_id=appointment.hospital_id,
            department=department,
            queue_number=queue_number,
            room="Room 101",
            position=position,
            status="WAITING",
        )

        db.session.add(queue)

    db.session.commit()


@queue_bp.route("/live-monitor")
def live_monitor():

    if not patient_required():
        return redirect(
            url_for("auth.login")
        )

    create_today_queues()

    return render_template(
        "live_monitor.html"
    )


@queue_bp.route("/api/queue")
def get_queue():

    if not patient_required():
        return {
            "error": "Unauthorized"
        }, 401

    create_today_queues()

    queues = QueueEntry.query.filter(
        QueueEntry.status.in_([
            "WAITING",
            "CALLED",
            "IN_CONSULTATION",
        ])
    ).order_by(
        QueueEntry.department.asc(),
        QueueEntry.position.asc()
    ).all()

    result = []

    for queue in queues:

        result.append({
            "id": queue.queue_entry_id,
            "queue_number": queue.queue_number,
            "department": queue.department,
            "patient_name": queue.patient.name,
            "room": queue.room,
            "position": queue.position,
            "status": queue.status,
        })

    return result


@queue_bp.route(
    "/api/queue/call-next",
    methods=["POST"]
)
def call_next_patient():

    if not patient_required():
        return {
            "success": False,
            "message": "Unauthorized",
        }, 401

    data = request.get_json(
        silent=True
    ) or {}

    department = data.get(
        "department"
    )

    if not department:
        return {
            "success": False,
            "message": "Department is required",
        }, 400

    current = QueueEntry.query.filter(
        QueueEntry.department == department,
        QueueEntry.status.in_([
            "CALLED",
            "IN_CONSULTATION",
        ])
    ).first()

    if current:

        return {
            "success": False,
            "message": (
                f"{current.queue_number} "
                "is still active."
            ),
        }, 400

    queue = QueueEntry.query.filter(
        QueueEntry.department == department,
        QueueEntry.status == "WAITING",
    ).order_by(
        QueueEntry.position.asc()
    ).first()

    if not queue:

        return {
            "success": False,
            "message": "No patients waiting.",
        }, 404

    queue.status = "CALLED"
    queue.called_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True,
        "queue_number": queue.queue_number,
    }


@queue_bp.route(
    "/api/queue/<int:queue_id>/consultation",
    methods=["POST"]
)
def start_consultation(queue_id):

    if not patient_required():
        return {
            "success": False,
            "message": "Unauthorized",
        }, 401

    queue = db.session.get(
        QueueEntry,
        queue_id
    )

    if queue is None:
        return {
            "success": False,
            "message": "Queue not found",
        }, 404

    queue.status = "IN_CONSULTATION"
    queue.consultation_started_at = (
        datetime.utcnow()
    )

    db.session.commit()

    return {
        "success": True
    }


@queue_bp.route(
    "/api/queue/<int:queue_id>/complete",
    methods=["POST"]
)
def complete_queue(queue_id):

    if not patient_required():
        return {
            "success": False,
            "message": "Unauthorized",
        }, 401

    queue = db.session.get(
        QueueEntry,
        queue_id
    )

    if queue is None:
        return {
            "success": False,
            "message": "Queue not found",
        }, 404

    queue.status = "COMPLETED"
    queue.completed_at = datetime.utcnow()

    db.session.commit()

    return {
        "success": True
    }