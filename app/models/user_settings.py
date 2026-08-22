from app.extensions import db


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    budget_alerts_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    goal_reminders_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "settings",
            uselist=False
        )
    )

    def __repr__(self):
        return f"<UserSettings user={self.user_id}>"