from datetime import date

from app.extensions import db
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.user_settings import UserSettings
from app.notifications.utils import create_notification


def generate_goal_notifications(user_id):

    user_settings = UserSettings.query.filter_by(
        user_id=user_id
    ).first()

    goal_reminders_enabled = (
        user_settings is None
        or user_settings.goal_reminders_enabled
    )

    # ----------------------------------------
    # Goal reminders disabled
    # ----------------------------------------

    if not goal_reminders_enabled:

        Notification.query.filter(
            Notification.user_id == user_id,
            Notification.goal_id.isnot(None),
            Notification.is_read == False,
            Notification.type == "goal_reminder"
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

        return


    today = date.today()

    goals = (
        Goal.query
        .filter_by(user_id=user_id)
        .all()
    )


    for goal in goals:

        days_remaining = (
            goal.target_date - today
        ).days


        # Completed goals do not need reminders.
        if goal.current_amount >= goal.target_amount:

            Notification.query.filter(
                Notification.user_id == user_id,
                Notification.goal_id == goal.id,
                Notification.is_read == False,
                Notification.type == "goal_reminder"
            ).delete(
                synchronize_session=False
            )

            continue


        # ----------------------------------------
        # Reminder window: 7 days or less
        # ----------------------------------------

        if 0 <= days_remaining <= 7:

            if days_remaining == 0:

                message = (
                    f'Your "{goal.name}" savings goal '
                    f'is due today.'
                )

            elif days_remaining == 1:

                message = (
                    f'Your "{goal.name}" savings goal '
                    f'is due tomorrow.'
                )

            else:

                message = (
                    f'Your "{goal.name}" savings goal '
                    f'is due in {days_remaining} days.'
                )


            title = "Goal Reminder"


            existing = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.goal_id == goal.id,
                Notification.is_read == False,
                Notification.type == "goal_reminder"
            ).first()


            if existing:

                existing.title = title
                existing.message = message


            else:

                create_notification(
                    user_id=user_id,
                    goal_id=goal.id,
                    title=title,
                    message=message,
                    notification_type="goal_reminder"
                )


        # ----------------------------------------
        # Outside reminder window
        # ----------------------------------------

        else:

            Notification.query.filter(
                Notification.user_id == user_id,
                Notification.goal_id == goal.id,
                Notification.is_read == False,
                Notification.type == "goal_reminder"
            ).delete(
                synchronize_session=False
            )


    db.session.commit()