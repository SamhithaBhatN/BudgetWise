from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.profile import profile
from app.profile.forms import (
    ProfileForm,
    ChangePasswordForm,
    SettingsForm
)
from app.models.user import User
from app.models.user_settings import UserSettings
from app.extensions import db


@profile.route("/", methods=["GET", "POST"])
@login_required
def index():

    profile_form = ProfileForm(
        obj=current_user
    )

    password_form = ChangePasswordForm()


    # ========================================
    # Update Profile
    # ========================================

    if profile_form.validate_on_submit():

        # Check username uniqueness
        existing_username = (
            User.query
            .filter(
                User.username == profile_form.username.data,
                User.id != current_user.id
            )
            .first()
        )

        if existing_username:

            profile_form.username.errors.append(
                "This username is already in use."
            )

            return render_template(
                "profile/index.html",
                form=profile_form,
                password_form=password_form
            )


        # Check email uniqueness
        existing_email = (
            User.query
            .filter(
                User.email == profile_form.email.data,
                User.id != current_user.id
            )
            .first()
        )

        if existing_email:

            profile_form.email.errors.append(
                "This email is already in use."
            )

            return render_template(
                "profile/index.html",
                form=profile_form,
                password_form=password_form
            )


        # Update user profile
        current_user.full_name = (
            profile_form.full_name.data
        )

        current_user.username = (
            profile_form.username.data
        )

        current_user.email = (
            profile_form.email.data
        )

        current_user.currency = (
            profile_form.currency.data
        )

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile.index")
        )


    return render_template(
        "profile/index.html",
        form=profile_form,
        password_form=password_form
    )


# ==========================================
# Change Password
# ==========================================

@profile.route(
    "/change-password",
    methods=["POST"]
)
@login_required
def change_password():

    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():

        # Verify current password
        if not current_user.check_password(
            password_form.current_password.data
        ):

            password_form.current_password.errors.append(
                "Current password is incorrect."
            )

            profile_form = ProfileForm(
                obj=current_user
            )

            return render_template(
                "profile/index.html",
                form=profile_form,
                password_form=password_form
            )


        # Update password
        current_user.set_password(
            password_form.new_password.data
        )

        db.session.commit()

        flash(
            "Password changed successfully!",
            "success"
        )

        return redirect(
            url_for("profile.index")
        )


    profile_form = ProfileForm(
        obj=current_user
    )

    return render_template(
        "profile/index.html",
        form=profile_form,
        password_form=password_form
    )


# ==========================================
# Settings
# ==========================================

@profile.route(
    "/settings",
    methods=["GET", "POST"]
)
@login_required
def settings():

    user_settings = UserSettings.query.filter_by(
        user_id=current_user.id
    ).first()


    # Create default settings for users
    # who do not have a settings record yet.
    if not user_settings:

        user_settings = UserSettings(
            user_id=current_user.id,
            budget_alerts_enabled=True,
            goal_reminders_enabled=True
        )

        db.session.add(user_settings)
        db.session.commit()


    form = SettingsForm(
        obj=user_settings
    )


    if form.validate_on_submit():

        user_settings.budget_alerts_enabled = (
            form.budget_alerts_enabled.data
        )

        user_settings.goal_reminders_enabled = (
            form.goal_reminders_enabled.data
        )

        db.session.commit()

        flash(
            "Settings updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile.settings")
        )


    return render_template(
        "profile/settings.html",
        form=form
    )