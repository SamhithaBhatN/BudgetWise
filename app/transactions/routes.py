from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.transactions import transactions
from app.transactions.forms import TransactionForm
from app.models.transaction import Transaction
from app.extensions import db

@transactions.route("/")
@login_required
def index():

    transactions_list = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    return render_template(
        "transactions/index.html",
        transactions=transactions_list
    )

@transactions.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():

    form = TransactionForm()

    if form.validate_on_submit():

        transaction = Transaction(
            title=form.title.data,
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data,
            date=form.date.data,
            note=form.note.data,
            user_id=current_user.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Transaction added successfully!", "success")

        return redirect(url_for("dashboard.home"))

    return render_template(
        "transactions/add_transaction.html",
        form=form
    )

@transactions.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id):

    transaction = Transaction.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():

        transaction.title = form.title.data
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.category = form.category.data
        transaction.date = form.date.data
        transaction.note = form.note.data

        db.session.commit()

        flash("Transaction updated successfully!", "success")

        return redirect(url_for("transactions.index"))

    return render_template(
        "transactions/edit_transaction.html",
        form=form
    )

@transactions.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_transaction(id):

    transaction = Transaction.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully!", "success")

    return redirect(url_for("transactions.index"))