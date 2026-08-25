from app.extensions import db
from app.models.user import User


def test_register_success(client, app):

    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "submit": "Create Account"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account created successfully!" in response.data

    with app.app_context():

        user = User.query.filter_by(
            email="test@example.com"
        ).first()

        assert user is not None
        assert user.username == "testuser"
        assert user.currency == "INR"
        assert user.check_password(
            "TestPassword123"
        )


def test_register_duplicate_username(client, app):

    with app.app_context():

        user = User(
            full_name="Existing User",
            username="existinguser",
            email="existing@example.com",
            currency="INR"
        )

        user.set_password("Password123")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/register",
        data={
            "full_name": "Another User",
            "username": "existinguser",
            "email": "another@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "submit": "Create Account"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Username already exists." in response.data


def test_register_duplicate_email(client, app):

    with app.app_context():

        user = User(
            full_name="Existing User",
            username="existinguser",
            email="existing@example.com",
            currency="INR"
        )

        user.set_password("Password123")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/register",
        data={
            "full_name": "Another User",
            "username": "anotheruser",
            "email": "existing@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "submit": "Create Account"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Email already registered." in response.data


def test_login_success(client, app):

    with app.app_context():

        user = User(
            full_name="Login User",
            username="loginuser",
            email="login@example.com",
            currency="INR"
        )

        user.set_password("TestPassword123")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "email": "login@example.com",
            "password": "TestPassword123",
            "submit": "Login"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Welcome back!" in response.data


def test_login_invalid_password(client, app):

    with app.app_context():

        user = User(
            full_name="Login User",
            username="loginuser",
            email="login@example.com",
            currency="INR"
        )

        user.set_password("CorrectPassword123")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "email": "login@example.com",
            "password": "WrongPassword123",
            "submit": "Login"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_logout(client, app):

    with app.app_context():

        user = User(
            full_name="Logout User",
            username="logoutuser",
            email="logout@example.com",
            currency="INR"
        )

        user.set_password("TestPassword123")

        db.session.add(user)
        db.session.commit()

    # Login
    client.post(
        "/login",
        data={
            "email": "logout@example.com",
            "password": "TestPassword123",
            "submit": "Login"
        }
    )

    # Logout
    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Logged out successfully!" in response.data 