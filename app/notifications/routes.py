from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.notifications import notifications
from app.notifications.forms import NotificationForm
from app.models.notification import Notification
from app.extensions import db


@notifications.route("/")
@login_required
def index():

    notifications_list = (
        Notification.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    form = NotificationForm()

    return render_template(
        "notifications/index.html",
        notifications=notifications_list,
        form=form
    )


@notifications.route(
    "/read/<int:id>",
    methods=["POST"]
)
@login_required
def mark_as_read(id):

    notification = Notification.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    form = NotificationForm()

    if not form.validate_on_submit():

        flash(
            "Invalid request.",
            "danger"
        )

        return redirect(
            url_for("notifications.index")
        )

    notification.is_read = True

    db.session.commit()

    flash(
        "Notification marked as read.",
        "success"
    )

    return redirect(
        url_for("notifications.index")
    )