import os

import pytest


# ----------------------------------------
# Configure test environment BEFORE
# importing the Flask application.
# ----------------------------------------

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


from app import create_app
from app.extensions import db


@pytest.fixture
def app():

    flask_app = create_app()

    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False
    )

    with flask_app.app_context():

        db.create_all()

        yield flask_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):

    return app.test_client()


@pytest.fixture
def runner(app):

    return app.test_cli_runner()