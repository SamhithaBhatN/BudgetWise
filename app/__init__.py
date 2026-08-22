from flask import Flask
from config import Config

from app.extensions import db, migrate, login_manager

from flask_login import current_user
from app.models.notification import Notification


def create_app():

    flask_app = Flask(__name__)

    flask_app.config.from_object(Config)

    # ----------------------------------------
    # Initialize Extensions
    # ----------------------------------------

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)


    # ----------------------------------------
    # Authentication Loader
    # ----------------------------------------

    import app.auth_loader


    # ----------------------------------------
    # Register Blueprints
    # ----------------------------------------

    from app.main import main
    flask_app.register_blueprint(main)

    from app.auth import auth
    flask_app.register_blueprint(auth)

    from app.dashboard import dashboard
    flask_app.register_blueprint(dashboard)

    from app.transactions import transactions
    flask_app.register_blueprint(transactions)

    from app.categories import categories
    flask_app.register_blueprint(categories)

    from app.budgets import budgets
    flask_app.register_blueprint(budgets)

    from app.goals import goals
    flask_app.register_blueprint(goals)

    from app.reports import reports
    flask_app.register_blueprint(reports)

    from app.notifications import notifications
    flask_app.register_blueprint(notifications)

    from app.profile import profile
    flask_app.register_blueprint(profile)

    # ----------------------------------------
    # Global Notification Count
    # ----------------------------------------

    @flask_app.context_processor
    def inject_notification_count():

        unread_notification_count = 0

        if current_user.is_authenticated:

            unread_notification_count = (
                Notification.query
                .filter_by(
                    user_id=current_user.id,
                    is_read=False
                )
                .count()
            )

        return {
            "unread_notification_count": unread_notification_count
        }


    return flask_app