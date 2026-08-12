from flask import render_template
from flask_login import login_required, current_user

from sqlalchemy import func

from app.dashboard import dashboard
from app.models.transaction import Transaction


@dashboard.route("/")
@login_required
def home():

    total_income = (
        Transaction.query
        .filter_by(user_id=current_user.id, type="Income")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
        or 0
    )

    total_expense = (
        Transaction.query
        .filter_by(user_id=current_user.id, type="Expense")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
        or 0
    )

    net_balance = total_income - total_expense

    transaction_count = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .count()
    )

    recent_transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        transaction_count=transaction_count,
        recent_transactions=recent_transactions
    )