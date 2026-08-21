from sqlalchemy import func

from app.extensions import db
from app.models.budget import Budget
from app.models.notification import Notification
from app.models.transaction import Transaction
from app.notifications.utils import create_notification


def generate_budget_notifications(user_id):

    budgets = (
        Budget.query
        .filter_by(user_id=user_id)
        .all()
    )

    for budget in budgets:

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
        # Budget Exceeded
        # ----------------------------------------

        if percentage >= 100:

            title = "Budget Exceeded"

            message = (
                f"Your {budget.category.name} budget for "
                f"{budget.month}/{budget.year} has been exceeded."
            )

            notification_type = "budget_exceeded"


        # ----------------------------------------
        # Budget Warning
        # ----------------------------------------

        elif percentage >= 80:

            title = "Budget Warning"

            message = (
                f"Your {budget.category.name} budget for "
                f"{budget.month}/{budget.year} is "
                f"{percentage:.1f}% used."
            )

            notification_type = "budget_warning"

        else:
            continue


        # ----------------------------------------
        # Prevent Duplicate Unread Notifications
        # ----------------------------------------

        existing = Notification.query.filter_by(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            is_read=False
        ).first()

        if not existing:

            create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type
            )


    db.session.commit()