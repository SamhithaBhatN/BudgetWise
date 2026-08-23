from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.dashboard import dashboard
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.goal import Goal
from app.models.notification import Notification


@dashboard.route("/")
@login_required
def home():

    # ========================================
    # Overall Financial Summary
    # ========================================

    total_income = (
        Transaction.query
        .filter_by(
            user_id=current_user.id,
            type="Income"
        )
        .with_entities(
            func.coalesce(
                func.sum(Transaction.amount),
                0
            )
        )
        .scalar()
    )

    total_expense = (
        Transaction.query
        .filter_by(
            user_id=current_user.id,
            type="Expense"
        )
        .with_entities(
            func.coalesce(
                func.sum(Transaction.amount),
                0
            )
        )
        .scalar()
    )

    total_income = float(total_income or 0)
    total_expense = float(total_expense or 0)

    net_balance = (
        total_income - total_expense
    )


    # ========================================
    # Transaction Count
    # ========================================

    transaction_count = (
        Transaction.query
        .filter_by(
            user_id=current_user.id
        )
        .count()
    )


    # ========================================
    # Recent Transactions
    # ========================================

    recent_transactions = (
        Transaction.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Transaction.date.desc()
        )
        .limit(5)
        .all()
    )


    # ========================================
    # Savings Goals Summary
    # ========================================

    goals_list = (
        Goal.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Goal.target_date.asc()
        )
        .all()
    )

    total_goal_target = sum(
        float(goal.target_amount)
        for goal in goals_list
    )

    total_goal_saved = sum(
        float(goal.current_amount)
        for goal in goals_list
    )

    total_goal_remaining = (
        total_goal_target - total_goal_saved
    )

    overall_goal_percentage = (
        (total_goal_saved / total_goal_target) * 100
        if total_goal_target > 0
        else 0
    )


    # ========================================
    # Budget Summary
    # ========================================

    budgets_list = (
        Budget.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )

    total_budget = sum(
        float(budget.amount)
        for budget in budgets_list
    )

    # Calculate total spending for all budgets
    total_budget_spent = 0

    for budget in budgets_list:

        spent = (
            db.session.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0
                )
            )
            .filter(
                Transaction.user_id == current_user.id,
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

        total_budget_spent += float(
            spent or 0
        )


    total_budget_remaining = (
        total_budget - total_budget_spent
    )

    overall_budget_percentage = (
        (total_budget_spent / total_budget) * 100
        if total_budget > 0
        else 0
    )


    # ========================================
    # Notifications
    # ========================================

    unread_notification_count = (
        Notification.query
        .filter_by(
            user_id=current_user.id,
            is_read=False
        )
        .count()
    )


    # ========================================
    # Render Dashboard
    # ========================================

    return render_template(
        "dashboard/dashboard.html",

        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        transaction_count=transaction_count,

        recent_transactions=recent_transactions,

        goals=goals_list,
        total_goal_target=total_goal_target,
        total_goal_saved=total_goal_saved,
        total_goal_remaining=total_goal_remaining,
        overall_goal_percentage=overall_goal_percentage,

        total_budget=total_budget,
        total_budget_spent=total_budget_spent,
        total_budget_remaining=total_budget_remaining,
        overall_budget_percentage=overall_budget_percentage,

        unread_notification_count=unread_notification_count
    )