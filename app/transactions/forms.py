from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    SelectField,
    DateField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired, NumberRange
from datetime import date


class TransactionForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[DataRequired()]
    )

    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01)
        ]
    )

    type = SelectField(
        "Transaction Type",
        choices=[
            ("Income", "Income"),
            ("Expense", "Expense")
        ],
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category",
        choices=[],
        validators=[DataRequired()]
    )

    date = DateField(
        "Date",
        default=date.today,
        validators=[DataRequired()]
    )

    note = TextAreaField("Note")

    submit = SubmitField("Save Transaction")

    def set_categories(self, categories):

        self.category.choices = [
            (category.name, category.name)
            for category in categories
        ]