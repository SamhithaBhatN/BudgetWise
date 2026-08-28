from datetime import date, timedelta

from app.extensions import db
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.user import User
from app.models.user_settings import UserSettings


def create_user(
    app,
    full_name,
    username,
    email,
    password="TestPassword123"
):

    with app.app_context():

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            currency="INR"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user.id


def login_user(
    client,
    email,
    password="TestPassword123"
):

    response = client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "submit": "Login"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Welcome back!" in response.data

    return response


def authenticate_user(
    client,
    user_id
):

    with client.session_transaction() as session:

        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def create_settings(
    app,
    user_id,
    budget_alerts_enabled=True,
    goal_reminders_enabled=True
):

    with app.app_context():

        settings = UserSettings(
            user_id=user_id,
            budget_alerts_enabled=budget_alerts_enabled,
            goal_reminders_enabled=goal_reminders_enabled
        )

        db.session.add(settings)
        db.session.commit()

        return settings.id


def create_goal(
    app,
    user_id,
    name="Laptop",
    target_amount=50000,
    current_amount=10000,
    target_date=None
):

    if target_date is None:

        target_date = (
            date.today() + timedelta(days=30)
        )

    with app.app_context():

        goal = Goal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date
        )

        db.session.add(goal)
        db.session.commit()

        return goal.id


def create_notification(
    app,
    user_id,
    title="Test Notification",
    message="Test notification message",
    notification_type="test"
):

    with app.app_context():

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type
        )

        db.session.add(notification)
        db.session.commit()

        return notification.id


def test_notifications_page_requires_login(client):

    response = client.get(
        "/notifications/"
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_notifications_page_shows_user_notifications(
    client,
    app
):

    user_id = create_user(
        app,
        "Notification User",
        "notificationuser",
        "notification@example.com"
    )

    login_user(
        client,
        "notification@example.com"
    )

    create_notification(
        app,
        user_id,
        title="Budget Warning",
        message="Your Food budget is 80% used.",
        notification_type="budget_warning"
    )

    response = client.get(
        "/notifications/"
    )

    assert response.status_code == 200
    assert b"Budget Warning" in response.data
    assert b"Your Food budget is 80% used." in response.data


def test_mark_notification_as_read(
    client,
    app
):

    user_id = create_user(
        app,
        "Read User",
        "readuser",
        "read@example.com"
    )

    login_user(
        client,
        "read@example.com"
    )

    notification_id = create_notification(
        app,
        user_id,
        title="Read Me",
        message="Please mark this notification as read.",
        notification_type="test"
    )

    response = client.post(
        f"/notifications/read/{notification_id}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Notification marked as read." in response.data

    with app.app_context():

        notification = db.session.get(
            Notification,
            notification_id
        )

        assert notification is not None
        assert notification.is_read is True


def test_user_cannot_mark_another_users_notification_as_read(
    client,
    app
):

    owner_id = create_user(
        app,
        "Notification Owner",
        "notificationowner",
        "notificationowner@example.com"
    )

    other_user_id = create_user(
        app,
        "Other User",
        "othernotificationuser",
        "othernotification@example.com"
    )

    notification_id = create_notification(
        app,
        owner_id,
        title="Private Notification",
        message="This belongs to another user.",
        notification_type="test"
    )

    authenticate_user(
        client,
        other_user_id
    )

    response = client.post(
        f"/notifications/read/{notification_id}"
    )

    assert response.status_code == 404

    with app.app_context():

        notification = db.session.get(
            Notification,
            notification_id
        )

        assert notification is not None
        assert notification.is_read is False


def test_goal_reminder_generated_within_seven_days(
    client,
    app
):

    user_id = create_user(
        app,
        "Reminder User",
        "reminderuser",
        "reminder@example.com"
    )

    create_settings(
        app,
        user_id,
        goal_reminders_enabled=True
    )

    goal_id = create_goal(
        app,
        user_id,
        name="Laptop",
        target_amount=50000,
        current_amount=10000,
        target_date=(
            date.today() + timedelta(days=3)
        )
    )

    login_user(
        client,
        "reminder@example.com"
    )

    # Goal reminder generation happens on /goals/
    response = client.get(
        "/goals/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            goal_id=goal_id,
            type="goal_reminder",
            is_read=False
        ).first()

        assert notification is not None
        assert notification.title == "Goal Reminder"
        assert "due in 3 days" in notification.message


def test_goal_reminder_due_tomorrow(
    client,
    app
):

    user_id = create_user(
        app,
        "Tomorrow User",
        "tomorrowuser",
        "tomorrow@example.com"
    )

    create_settings(
        app,
        user_id,
        goal_reminders_enabled=True
    )

    goal_id = create_goal(
        app,
        user_id,
        name="Trip",
        target_amount=30000,
        current_amount=5000,
        target_date=(
            date.today() + timedelta(days=1)
        )
    )

    login_user(
        client,
        "tomorrow@example.com"
    )

    # Goal reminder generation happens on /goals/
    response = client.get(
        "/goals/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            goal_id=goal_id,
            type="goal_reminder",
            is_read=False
        ).first()

        assert notification is not None
        assert "due tomorrow" in notification.message


def test_completed_goal_does_not_generate_reminder(
    client,
    app
):

    user_id = create_user(
        app,
        "Completed User",
        "completeduser",
        "completed@example.com"
    )

    create_settings(
        app,
        user_id,
        goal_reminders_enabled=True
    )

    goal_id = create_goal(
        app,
        user_id,
        name="Completed Goal",
        target_amount=20000,
        current_amount=20000,
        target_date=(
            date.today() + timedelta(days=2)
        )
    )

    login_user(
        client,
        "completed@example.com"
    )

    # Goal reminder generation happens on /goals/
    response = client.get(
        "/goals/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            goal_id=goal_id,
            type="goal_reminder"
        ).first()

        assert notification is None


def test_goal_reminders_disabled(
    client,
    app
):

    user_id = create_user(
        app,
        "Disabled User",
        "disableduser",
        "disabled@example.com"
    )

    create_settings(
        app,
        user_id,
        goal_reminders_enabled=False
    )

    goal_id = create_goal(
        app,
        user_id,
        name="Disabled Reminder Goal",
        target_amount=20000,
        current_amount=5000,
        target_date=(
            date.today() + timedelta(days=3)
        )
    )

    login_user(
        client,
        "disabled@example.com"
    )

    # Goal reminder generation happens on /goals/
    response = client.get(
        "/goals/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            goal_id=goal_id,
            type="goal_reminder"
        ).first()

        assert notification is None


def test_old_goal_reminder_is_removed_outside_window(
    client,
    app
):

    user_id = create_user(
        app,
        "Old Reminder User",
        "oldreminderuser",
        "oldreminder@example.com"
    )

    create_settings(
        app,
        user_id,
        goal_reminders_enabled=True
    )

    goal_id = create_goal(
        app,
        user_id,
        name="Future Goal",
        target_amount=40000,
        current_amount=5000,
        target_date=(
            date.today() + timedelta(days=30)
        )
    )

    with app.app_context():

        notification = Notification(
            user_id=user_id,
            goal_id=goal_id,
            title="Goal Reminder",
            message="Old reminder",
            type="goal_reminder",
            is_read=False
        )

        db.session.add(notification)
        db.session.commit()

    login_user(
        client,
        "oldreminder@example.com"
    )

    # Goal reminder generation happens on /goals/
    response = client.get(
        "/goals/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            goal_id=goal_id,
            type="goal_reminder",
            is_read=False
        ).first()

        assert notification is None


def test_user_cannot_see_another_users_notifications(
    client,
    app
):

    owner_id = create_user(
        app,
        "Owner User",
        "notificationowner2",
        "notificationowner2@example.com"
    )

    other_user_id = create_user(
        app,
        "Other User",
        "notificationother2",
        "notificationother2@example.com"
    )

    create_notification(
        app,
        owner_id,
        title="Private Alert",
        message="This should not be visible.",
        notification_type="test"
    )

    authenticate_user(
        client,
        other_user_id
    )

    response = client.get(
        "/notifications/"
    )

    assert response.status_code == 200
    assert b"Private Alert" not in response.data