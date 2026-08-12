from datetime import datetime

from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

    type = db.Column(
        db.String(20),
        nullable=False
    )  # Income or Expense

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Category {self.name}>"