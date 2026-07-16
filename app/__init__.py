from flask import Flask
from config import Config

from app.extensions import db, migrate, login_manager


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)

    import app.auth_loader

    from app.main import main
    flask_app.register_blueprint(main)

    from app.auth import auth
    flask_app.register_blueprint(auth)

    return flask_app