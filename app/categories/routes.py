from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.categories import categories
from app.categories.forms import CategoryForm
from app.models.category import Category
from app.models.transaction import Transaction
from app.extensions import db


@categories.route("/")
@login_required
def index():

    categories_list = (
        Category.query
        .filter_by(user_id=current_user.id)
        .order_by(Category.name.asc())
        .all()
    )

    form = CategoryForm()

    return render_template(
        "categories/index.html",
        categories=categories_list,
        form=form
    )


@categories.route("/add", methods=["POST"])
@login_required
def add_category():

    form = CategoryForm()

    if form.validate_on_submit():

        category = Category(
            name=form.name.data,
            type=form.type.data,
            user_id=current_user.id
        )

        db.session.add(category)
        db.session.commit()

        flash("Category added successfully!", "success")

    return redirect(url_for("categories.index"))

@categories.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):

    category = Category.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    form = CategoryForm(obj=category)

    if form.validate_on_submit():

        category.name = form.name.data
        category.type = form.type.data

        db.session.commit()

        flash("Category updated successfully!", "success")

        return redirect(url_for("categories.index"))

    return render_template(
        "categories/edit_category.html",
        form=form,
        category=category
    )

@categories.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_category(id):

    category = Category.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    # Check whether this category is being used
    # by any existing transaction.

    transaction_exists = Transaction.query.filter_by(
        user_id=current_user.id,
        category=category.name
    ).first()

    if transaction_exists:

        flash(
            f'Cannot delete "{category.name}" because it is being used by existing transactions.',
            "danger"
        )

        return redirect(url_for("categories.index"))

    db.session.delete(category)
    db.session.commit()

    flash(
        f'Category "{category.name}" deleted successfully!',
        "success"
    )

    return redirect(url_for("categories.index"))