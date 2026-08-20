from datetime import date

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from app.budgets import budgets
from app.budgets.forms import BudgetForm
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.extensions import db


@budgets.route("/", methods=["GET", "POST"])
@login_required
def index():

    form = BudgetForm()

    # Get only the current user's expense categories
    expense_categories = (
        Category.query
        .filter_by(
            user_id=current_user.id,
            type="Expense"
        )
        .order_by(Category.name.asc())
        .all()
    )

    # Populate category choices
    form.category_id.choices = [
        (category.id, category.name)
        for category in expense_categories
    ]

    # Get all budgets belonging to the current user
    budgets_list = (
        Budget.query
        .filter_by(user_id=current_user.id)
        .order_by(
            Budget.year.desc(),
            Budget.month.desc()
        )
        .all()
    )

    # Calculate spending information for each budget
    budget_data = []

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

        spent = float(spent or 0)

        budget_amount = float(budget.amount)

        remaining = budget_amount - spent

        percentage = (
            (spent / budget_amount) * 100
            if budget_amount > 0
            else 0
        )

        budget_data.append(
            {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage
            }
        )

    # ----------------------------------------
    # Add Budget
    # ----------------------------------------

    if form.validate_on_submit():

        today = date.today()

        selected_year = form.year.data
        selected_month = form.month.data

        # Prevent budgets for past months
        if (
            selected_year < today.year
            or (
                selected_year == today.year
                and selected_month < today.month
            )
        ):

            flash(
                "You cannot create a budget for a month that has already passed.",
                "danger"
            )

            return render_template(
                "budgets/index.html",
                form=form,
                budgets=budget_data
            )

        # Prevent duplicate budgets
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category_id.data,
            month=form.month.data,
            year=form.year.data
        ).first()

        if existing_budget:

            flash(
                "A budget already exists for this category and month.",
                "danger"
            )

            return render_template(
                "budgets/index.html",
                form=form,
                budgets=budget_data
            )

        # Create budget
        budget = Budget(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            month=form.month.data,
            year=form.year.data
        )

        db.session.add(budget)
        db.session.commit()

        flash(
            "Budget added successfully!",
            "success"
        )

        return redirect(
            url_for("budgets.index")
        )

    return render_template(
        "budgets/index.html",
        form=form,
        budgets=budget_data
    )


# ==========================================
# Edit Budget
# ==========================================

@budgets.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_budget(id):

    # Find only the current user's budget
    budget = Budget.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    # Pre-fill form
    form = BudgetForm(obj=budget)

    # Get current user's expense categories
    expense_categories = (
        Category.query
        .filter_by(
            user_id=current_user.id,
            type="Expense"
        )
        .order_by(Category.name.asc())
        .all()
    )

    # Populate category choices
    form.category_id.choices = [
        (category.id, category.name)
        for category in expense_categories
    ]

    if form.validate_on_submit():

        today = date.today()

        selected_year = form.year.data
        selected_month = form.month.data

        # Prevent moving budget to past month
        if (
            selected_year < today.year
            or (
                selected_year == today.year
                and selected_month < today.month
            )
        ):

            flash(
                "You cannot set a budget for a month that has already passed.",
                "danger"
            )

            return render_template(
                "budgets/edit_budget.html",
                form=form
            )

        # Prevent duplicates while excluding
        # the budget currently being edited
        duplicate_budget = Budget.query.filter(
            Budget.user_id == current_user.id,
            Budget.category_id == form.category_id.data,
            Budget.month == form.month.data,
            Budget.year == form.year.data,
            Budget.id != budget.id
        ).first()

        if duplicate_budget:

            flash(
                "Another budget already exists for this category and month.",
                "danger"
            )

            return render_template(
                "budgets/edit_budget.html",
                form=form
            )

        # Update budget
        budget.category_id = form.category_id.data
        budget.amount = form.amount.data
        budget.month = form.month.data
        budget.year = form.year.data

        db.session.commit()

        flash(
            "Budget updated successfully!",
            "success"
        )

        return redirect(
            url_for("budgets.index")
        )

    return render_template(
        "budgets/edit_budget.html",
        form=form
    )


# ==========================================
# Delete Budget
# ==========================================

@budgets.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@login_required
def delete_budget(id):

    # Find only the current user's budget
    budget = Budget.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(budget)
    db.session.commit()

    flash(
        "Budget deleted successfully!",
        "success"
    )

    return redirect(
        url_for("budgets.index")
    )