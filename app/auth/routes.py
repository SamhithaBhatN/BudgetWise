import os
import smtplib
from email.message import EmailMessage

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import (
    login_user,
    login_required,
    logout_user,
)
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)

from app.auth import auth
from app.auth.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from app.extensions import db
from app.models.user import User


RESET_TOKEN_MAX_AGE = 3600


def get_reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="budgetwise-password-reset"
    )


def generate_reset_token(user):
    serializer = get_reset_serializer()

    return serializer.dumps({
        "user_id": user.id,
        "password_hash": user.password_hash,
    })


def verify_reset_token(token):
    serializer = get_reset_serializer()

    try:
        data = serializer.loads(
            token,
            max_age=RESET_TOKEN_MAX_AGE
        )
    except SignatureExpired:
        return None
    except BadSignature:
        return None

    user = db.session.get(
        User,
        data.get("user_id")
    )

    if user is None:
        return None

    if user.password_hash != data.get("password_hash"):
        return None

    return user


def send_password_reset_email(user, reset_url):
    smtp_server = current_app.config.get(
        "MAIL_SERVER"
    )
    smtp_port = current_app.config.get(
        "MAIL_PORT"
    )
    smtp_username = current_app.config.get(
        "MAIL_USERNAME"
    )
    smtp_password = current_app.config.get(
        "MAIL_PASSWORD"
    )
    sender = current_app.config.get(
        "MAIL_DEFAULT_SENDER"
    )

    if not all([
        smtp_server,
        smtp_port,
        smtp_username,
        smtp_password,
        sender,
    ]):
        current_app.logger.error(
            "Password reset email configuration is incomplete."
        )

        return False

    message = EmailMessage()

    message["Subject"] = "BudgetWise Password Reset"
    message["From"] = sender
    message["To"] = user.email

    message.set_content(
        f"""Hello {user.full_name},

We received a request to reset your BudgetWise password.

Use the following link to reset your password:

{reset_url}

This link is valid for 1 hour.

If you did not request a password reset, you can safely ignore this email.

Regards,
BudgetWise
"""
    )

    try:

        with smtplib.SMTP(
            smtp_server,
            smtp_port,
            timeout=30
        ) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(message)

        return True

    except (
        OSError,
        smtplib.SMTPException,
    ) as exc:

        current_app.logger.exception(
            "Failed to send password reset email: %s",
            exc
        )

        return False


@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            login_user(user)

            flash(
                "Welcome back!",
                "success"
            )

            return redirect(
                url_for("dashboard.home")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "danger"
            )

            return render_template(
                "auth/register.html",
                form=form
            )

        existing_email = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_email:

            flash(
                "Email already registered.",
                "danger"
            )

            return render_template(
                "auth/register.html",
                form=form
            )

        user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data,
            currency="INR"
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully! Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html",
        form=form
    )


@auth.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    form = ForgotPasswordForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.is_active:

            token = generate_reset_token(
                user
            )

            reset_url = url_for(
                "auth.reset_password",
                token=token,
                _external=True
            )

            send_password_reset_email(
                user,
                reset_url
            )

        # Keep the response identical for
        # registered and unregistered emails
        # to avoid account enumeration.
        flash(
            "If an account with that email exists, "
            "a password reset link has been sent.",
            "info"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/forgot_password.html",
        form=form
    )


@auth.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    user = verify_reset_token(
        token
    )

    if user is None:

        flash(
            "The password reset link is invalid or has expired.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    form = ResetPasswordForm()

    if form.validate_on_submit():

        user.set_password(
            form.password.data
        )

        db.session.commit()

        flash(
            "Your password has been reset successfully. "
            "Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/reset_password.html",
        form=form
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully!",
        "success"
    )

    return redirect(
        url_for("main.home")
    )