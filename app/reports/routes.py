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
        # Six-Month Trend
        #
        # The selected month is the final month
        # in the six-month reporting period.
        # ----------------------------------------

        trend_data = []

        month_names = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        # Start five months before the selected month.
        trend_month = selected_month - 5
        trend_year = selected_year

        while trend_month <= 0:

            trend_month += 12
            trend_year -= 1

        for _ in range(6):

            month_income = (
                Transaction.query
                .filter(
                    Transaction.user_id == current_user.id,
                    Transaction.type == "Income",
                    func.extract(
                        "month",
                        Transaction.date
                    ) == trend_month,
                    func.extract(
                        "year",
                        Transaction.date
                    ) == trend_year
                )
                .with_entities(
                    func.coalesce(
                        func.sum(Transaction.amount),
                        0
                    )
                )
                .scalar()
            )

            month_expense = (
                Transaction.query
                .filter(
                    Transaction.user_id == current_user.id,
                    Transaction.type == "Expense",
                    func.extract(
                        "month",
                        Transaction.date
                    ) == trend_month,
                    func.extract(
                        "year",
                        Transaction.date
                    ) == trend_year
                )
                .with_entities(
                    func.coalesce(
                        func.sum(Transaction.amount),
                        0
                    )
                )
                .scalar()
            )

            trend_data.append(
                {
                    "month": trend_month,
                    "year": trend_year,
                    "label": (
                        f"{month_names[trend_month][:3]} "
                        f"{trend_year}"
                    ),
                    "income": float(month_income or 0),
                    "expense": float(month_expense or 0)
                }
            )

            # Move to the next month.
            trend_month += 1

            if trend_month > 12:

                trend_month = 1
                trend_year += 1

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
            "category_expenses": category_expenses_data,
            "trend": trend_data
        }

    return render_template(
        "reports/index.html",
        form=form,
        report=report_data
    )