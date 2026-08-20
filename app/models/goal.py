from datetime import datetime

from app.extensions import db


class Goal(db.Model):
    __tablename__ = "goals"

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
        db.String(100),
        nullable=False
    )

    target_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    current_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    target_date = db.Column(
        db.Date,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="goals"
    )

    def __repr__(self):
        return f"<Goal {self.name}>"