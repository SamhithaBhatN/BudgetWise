from datetime import datetime

from app.extensions import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(14, 2),
        nullable=False
    )

    type = db.Column(
        db.String(20),
        nullable=False
    )  # Income or Expense

    category = db.Column(
        db.String(50),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    note = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Transaction {self.title}>"