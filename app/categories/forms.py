from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):

    name = StringField(
        "Category Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50)
        ]
    )

    type = SelectField(
        "Type",
        choices=[
            ("Expense", "Expense"),
            ("Income", "Income")
        ],
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Add Category")