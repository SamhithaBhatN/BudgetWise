from flask import render_template, redirect, url_for, flash
from flask_login import login_user

from app.auth import auth
from app.auth.forms import RegisterForm, LoginForm
from app.extensions import db
from app.models.user import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(form.password.data):

            login_user(user)

            flash("Welcome back!", "success")

            return redirect(url_for("main.home"))

        flash("Invalid email or password.", "danger")

    return render_template(
        "auth/login.html",
        form=form
    )

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:
            flash("Username already exists.", "danger")
            return render_template("auth/register.html", form=form)

        existing_email = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_email:
            flash("Email already registered.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data,
            currency="INR"
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)