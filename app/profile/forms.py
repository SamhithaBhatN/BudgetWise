from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    PasswordField,
    BooleanField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo
)


class ProfileForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    currency = SelectField(
        "Currency",
        choices=[
            ("INR", "Indian Rupee (₹)"),
            ("USD", "US Dollar ($)"),
            ("EUR", "Euro (€)"),
            ("GBP", "British Pound (£)")
        ],
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Save Changes"
    )


class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired()
        ]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                max=128
            )
        ]
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo(
                "new_password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField(
        "Change Password"
    )


class SettingsForm(FlaskForm):

    budget_alerts_enabled = BooleanField(
        "Budget Alerts"
    )

    goal_reminders_enabled = BooleanField(
        "Goal Reminders"
    )

    submit = SubmitField(
        "Save Settings"
    )