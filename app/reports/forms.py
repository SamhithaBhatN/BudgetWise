from datetime import date

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ReportForm(FlaskForm):

    month = SelectField(
        "Month",
        coerce=int,
        choices=[
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December")
        ],
        validators=[DataRequired()]
    )

    year = IntegerField(
        "Year",
        validators=[
            DataRequired(),
            NumberRange(min=2020, max=2100)
        ]
    )

    submit = SubmitField("Generate Report")