from datetime import date

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.budgets import budgets
from app.budgets.forms import BudgetForm
from app.models.budget import Budget
from app.models.category import Category
from app.extensions import db


@budgets.route("/", methods=["GET", "POST"])
@login_required
def index():

    form = BudgetForm()

    expense_categories = (
        Category.query
        .filter_by(
            user_id=current_user.id,
            type="Expense"
        )
        .order_by(Category.name.asc())
        .all()
    )

    form.category_id.choices = [
        (category.id, category.name)
        for category in expense_categories
    ]

    budgets_list = (
        Budget.query
        .filter_by(user_id=current_user.id)
        .order_by(
            Budget.year.desc(),
            Budget.month.desc()
        )
        .all()
    )

    if form.validate_on_submit():

        today = date.today()

        selected_year = form.year.data
        selected_month = form.month.data

        # Prevent creating budgets for past months.
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
                budgets=budgets_list
            )

        # Prevent duplicate budgets for the same
        # user, category, month, and year.
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
                budgets=budgets_list
            )

        budget = Budget(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            month=form.month.data,
            year=form.year.data
        )

        db.session.add(budget)
        db.session.commit()

        flash("Budget added successfully!", "success")

        return redirect(url_for("budgets.index"))

    return render_template(
        "budgets/index.html",
        form=form,
        budgets=budgets_list
    )


@budgets.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_budget(id):

    budget = Budget.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    form = BudgetForm(obj=budget)

    expense_categories = (
        Category.query
        .filter_by(
            user_id=current_user.id,
            type="Expense"
        )
        .order_by(Category.name.asc())
        .all()
    )

    form.category_id.choices = [
        (category.id, category.name)
        for category in expense_categories
    ]

    if form.validate_on_submit():

        today = date.today()

        selected_year = form.year.data
        selected_month = form.month.data

        # Prevent moving a budget to a past month.
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

        # Prevent duplicate budgets while excluding
        # the budget currently being edited.
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

        budget.category_id = form.category_id.data
        budget.amount = form.amount.data
        budget.month = form.month.data
        budget.year = form.year.data

        db.session.commit()

        flash("Budget updated successfully!", "success")

        return redirect(url_for("budgets.index"))

    return render_template(
        "budgets/edit_budget.html",
        form=form
    )


@budgets.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_budget(id):

    budget = Budget.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(budget)
    db.session.commit()

    flash("Budget deleted successfully!", "success")

    return redirect(url_for("budgets.index"))