from sqlalchemy import func

from app.extensions import db
from app.models.budget import Budget
from app.models.notification import Notification
from app.models.transaction import Transaction
from app.models.user_settings import UserSettings
from app.notifications.utils import create_notification


def generate_budget_notifications(user_id):

    # ----------------------------------------
    # Get user notification settings
    # ----------------------------------------

    user_settings = UserSettings.query.filter_by(
        user_id=user_id
    ).first()


    # If settings do not exist, use the default:
    # Budget alerts enabled.
    budget_alerts_enabled = (
        user_settings is None
        or user_settings.budget_alerts_enabled
    )


    # ----------------------------------------
    # Budget Alerts Disabled
    # ----------------------------------------

    if not budget_alerts_enabled:

        # Remove active unread budget alerts.
        Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.type.in_([
                "budget_warning",
                "budget_exceeded"
            ])
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

        return


    # ----------------------------------------
    # Get User Budgets
    # ----------------------------------------

    budgets = (
        Budget.query
        .filter_by(user_id=user_id)
        .all()
    )


    for budget in budgets:

        # ----------------------------------------
        # Calculate Spending
        # ----------------------------------------

        spent = (
            db.session.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "Expense",
                Transaction.category == budget.category.name
            )
            .filter(
                func.extract(
                    "month",
                    Transaction.date
                ) == budget.month,
                func.extract(
                    "year",
                    Transaction.date
                ) == budget.year
            )
            .scalar()
        )

        spent = float(spent or 0)
        budget_amount = float(budget.amount)


        if budget_amount <= 0:
            continue


        percentage = (
            spent / budget_amount
        ) * 100


        # ----------------------------------------
        # Below Warning Threshold
        # ----------------------------------------

        if percentage < 80:

            Notification.query.filter(
                Notification.user_id == user_id,
                Notification.budget_id == budget.id,
                Notification.is_read == False,
                Notification.type.in_([
                    "budget_warning",
                    "budget_exceeded"
                ])
            ).delete(
                synchronize_session=False
            )

            continue


        # ----------------------------------------
        # Determine Current Alert
        # ----------------------------------------

        if percentage >= 100:

            title = "Budget Exceeded"

            message = (
                f"Your {budget.category.name} budget for "
                f"{budget.month}/{budget.year} has been exceeded."
            )

            notification_type = "budget_exceeded"

        else:

            title = "Budget Warning"

            message = (
                f"Your {budget.category.name} budget for "
                f"{budget.month}/{budget.year} is "
                f"{percentage:.1f}% used."
            )

            notification_type = "budget_warning"


        # ----------------------------------------
        # Find Existing Active Notification
        # ----------------------------------------

        existing = Notification.query.filter(
            Notification.user_id == user_id,
            Notification.budget_id == budget.id,
            Notification.is_read == False,
            Notification.type.in_([
                "budget_warning",
                "budget_exceeded"
            ])
        ).first()


        # ----------------------------------------
        # Update Existing Notification
        # ----------------------------------------

        if existing:

            existing.title = title
            existing.message = message
            existing.type = notification_type


        # ----------------------------------------
        # Create New Notification
        # ----------------------------------------

        else:

            create_notification(
                user_id=user_id,
                budget_id=budget.id,
                title=title,
                message=message,
                notification_type=notification_type
            )


    db.session.commit()