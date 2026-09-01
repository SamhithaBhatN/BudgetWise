from app.extensions import db
from app.models.user import User
from app.auth import routes


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

    client.post(
        "/login",
        data={
            "email": "logout@example.com",
            "password": "TestPassword123",
            "submit": "Login"
        }
    )

    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Logged out successfully!" in response.data


def test_forgot_password_existing_email(
    client,
    app,
    monkeypatch
):

    with app.app_context():

        user = User(
            full_name="Reset User",
            username="resetuser",
            email="reset@example.com",
            currency="INR"
        )

        user.set_password("OldPassword123")

        db.session.add(user)
        db.session.commit()

    sent = {}

    def fake_send_email(user, reset_url):

        sent["email"] = user.email
        sent["url"] = reset_url

        return True

    monkeypatch.setattr(
        routes,
        "send_password_reset_email",
        fake_send_email
    )

    response = client.post(
        "/forgot-password",
        data={
            "email": "reset@example.com",
            "submit": "Send Reset Link"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"If an account with that email exists"
        in response.data
    )

    assert sent["email"] == "reset@example.com"
    assert "/reset-password/" in sent["url"]


def test_forgot_password_unknown_email(
    client,
    monkeypatch
):

    called = {
        "value": False
    }

    def fake_send_email(user, reset_url):

        called["value"] = True
        return True

    monkeypatch.setattr(
        routes,
        "send_password_reset_email",
        fake_send_email
    )

    response = client.post(
        "/forgot-password",
        data={
            "email": "unknown@example.com",
            "submit": "Send Reset Link"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"If an account with that email exists"
        in response.data
    )

    assert called["value"] is False


def test_reset_password_success(
    client,
    app
):

    with app.app_context():

        user = User(
            full_name="Reset User",
            username="resetuser",
            email="reset@example.com",
            currency="INR"
        )

        user.set_password("OldPassword123")

        db.session.add(user)
        db.session.commit()

        token = routes.generate_reset_token(
            user
        )

        user_id = user.id

    response = client.post(
        f"/reset-password/{token}",
        data={
            "password": "NewPassword123",
            "confirm_password": "NewPassword123",
            "submit": "Reset Password"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Your password has been reset successfully."
        in response.data
    )

    with app.app_context():

        user = db.session.get(
            User,
            user_id
        )

        assert user.check_password(
            "NewPassword123"
        )

        assert not user.check_password(
            "OldPassword123"
        )


def test_reset_password_token_invalid_after_password_change(
    client,
    app
):

    with app.app_context():

        user = User(
            full_name="Reset User",
            username="resetuser",
            email="reset@example.com",
            currency="INR"
        )

        user.set_password("OldPassword123")

        db.session.add(user)
        db.session.commit()

        token = routes.generate_reset_token(
            user
        )

        user.set_password(
            "AnotherPassword123"
        )

        db.session.commit()

    response = client.get(
        f"/reset-password/{token}",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"The password reset link is invalid or has expired."
        in response.data
    )


def test_reset_password_invalid_token(
    client
):

    response = client.get(
        "/reset-password/invalid-token",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"The password reset link is invalid or has expired."
        in response.data
    )


def test_forgot_password_page(client):

    response = client.get(
        "/forgot-password"
    )

    assert response.status_code == 200
    assert b"Forgot Password?" in response.data
    assert b"Send Reset Link" in response.data