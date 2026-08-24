import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():

    flask_app = create_app()

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key"
    )

    with flask_app.app_context():

        db.create_all()

        yield flask_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):

    return app.test_client()