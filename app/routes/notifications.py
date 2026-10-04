from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)

from app.extensions import db
from app.models.notification import Notification


notifications_bp = Blueprint(
    "notifications",
    __name__
)


@notifications_bp.route("/notifications")
def notifications():

    if "patient_id" not in session:
        return redirect(
            url_for("auth.login")
        )

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
        unread_count=unread_count,
    )


@notifications_bp.route(
    "/notifications/<int:notification_id>/read",
    methods=["POST"]
)
def mark_notification_read(
    notification_id
):

    if "patient_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    notification = db.session.get(
        Notification,
        notification_id
    )

    if notification is None:
        return redirect(
            url_for("notifications.notifications")
        )

    if (
        notification.patient_id
        != session["patient_id"]
    ):
        return redirect(
            url_for("notifications.notifications")
        )

    notification.is_read = True

    db.session.commit()

    return redirect(
        url_for(
            "notifications.notifications"
        )
    )


@notifications_bp.route(
    "/notifications/read-all",
    methods=["POST"]
)
def mark_all_notifications_read():

    if "patient_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    Notification.query.filter_by(
        patient_id=session["patient_id"],
        is_read=False,
    ).update(
        {
            "is_read": True
        }
    )

    db.session.commit()

    return redirect(
        url_for(
            "notifications.notifications"
        )
    )