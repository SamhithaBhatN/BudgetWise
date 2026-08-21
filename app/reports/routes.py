from datetime import date

from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.reports import reports
from app.reports.forms import ReportForm
from app.models.transaction import Transaction


@reports.route("/", methods=["GET", "POST"])
@login_required
def index():

    form = ReportForm()

    today = date.today()

    # Set current month and year as defaults
    if not form.is_submitted():
        form.month.data = today.month
        form.year.data = today.year

    report_data = None

    if form.validate_on_submit():

        selected_month = form.month.data
        selected_year = form.year.data

        # ----------------------------------------
        # Total Income
        # ----------------------------------------

        total_income = (
            Transaction.query
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "Income",
                func.extract(
                    "month",
                    Transaction.date
                ) == selected_month,
                func.extract(
                    "year",
                    Transaction.date
                ) == selected_year
            )
            .with_entities(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0
                )
            )
            .scalar()
        )

        # ----------------------------------------
        # Total Expenses
        # ----------------------------------------

        total_expense = (
            Transaction.query
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "Expense",
                func.extract(
                    "month",
                    Transaction.date
                ) == selected_month,
                func.extract(
                    "year",
                    Transaction.date
                ) == selected_year
            )
            .with_entities(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0
                )
            )
            .scalar()
        )

        # ----------------------------------------
        # Transaction Count
        # ----------------------------------------

        transaction_count = (
            Transaction.query
            .filter(
                Transaction.user_id == current_user.id,
                func.extract(
                    "month",
                    Transaction.date
                ) == selected_month,
                func.extract(
                    "year",
                    Transaction.date
                ) == selected_year
            )
            .count()
        )

        # ----------------------------------------
        # Category-wise Expenses
        # ----------------------------------------

        category_expenses = (
            Transaction.query
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "Expense",
                func.extract(
                    "month",
                    Transaction.date
                ) == selected_month,
                func.extract(
                    "year",
                    Transaction.date
                ) == selected_year
            )
            .with_entities(
                Transaction.category,
                func.sum(Transaction.amount)
            )
            .group_by(
                Transaction.category
            )
            .order_by(
                func.sum(Transaction.amount).desc()
            )
            .all()
        )

        # Convert database values into
        # template-friendly dictionaries.
        category_expenses_data = [
            {
                "category": category,
                "amount": float(amount)
            }
            for category, amount in category_expenses
        ]

        # ----------------------------------------
        # Convert totals to float
        # ----------------------------------------

        total_income = float(
            total_income or 0
        )

        total_expense = float(
            total_expense or 0
        )

        # ----------------------------------------
        # Net Balance
        # ----------------------------------------

        net_balance = (
            total_income - total_expense
        )

        # ----------------------------------------
        # Report Data
        # ----------------------------------------

        report_data = {
            "month": selected_month,
            "year": selected_year,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "transaction_count": transaction_count,
            "category_expenses": category_expenses_data
        }

    return render_template(
        "reports/index.html",
        form=form,
        report=report_data
    )