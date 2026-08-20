from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    DateField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Length,
    ValidationError
)


class GoalForm(FlaskForm):

    name = StringField(
        "Goal Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    target_amount = DecimalField(
        "Target Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01)
        ]
    )

    current_amount = DecimalField(
        "Current Amount",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    target_date = DateField(
        "Target Date",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Add Goal")

    def validate_current_amount(self, field):

        if (
            self.target_amount.data is not None
            and field.data is not None
            and field.data > self.target_amount.data
        ):
            raise ValidationError(
                "Current amount cannot be greater than the target amount."
            )

    def validate_target_date(self, field):

        if field.data and field.data < date.today():

            raise ValidationError(
                "Target date cannot be in the past."
            )