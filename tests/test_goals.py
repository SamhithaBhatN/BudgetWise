from datetime import date, timedelta

from app.extensions import db
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.user import User


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


def authenticate_user(client, user_id):

    with client.session_transaction() as session:

        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_add_goal_success(client, app):

    user_id = create_user(
        app,
        "Goal User",
        "goaluser",
        "goal@example.com"
    )

    login_user(
        client,
        "goal@example.com"
    )

    target_date = date.today() + timedelta(days=30)

    response = client.post(
        "/goals/",
        data={
            "name": "New Laptop",
            "target_amount": "65000",
            "current_amount": "24000",
            "target_date": target_date.isoformat(),
            "submit": "Add Goal"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Savings goal added successfully!" in response.data

    with app.app_context():

        goal = Goal.query.filter_by(
            user_id=user_id,
            name="New Laptop"
        ).first()

        assert goal is not None
        assert float(goal.target_amount) == 65000.00
        assert float(goal.current_amount) == 24000.00
        assert goal.target_date == target_date


def test_current_amount_cannot_exceed_target(
    client,
    app
):

    create_user(
        app,
        "Validation User",
        "validationgoaluser",
        "validationgoal@example.com"
    )

    login_user(
        client,
        "validationgoal@example.com"
    )

    target_date = date.today() + timedelta(days=30)

    response = client.post(
        "/goals/",
        data={
            "name": "Invalid Goal",
            "target_amount": "10000",
            "current_amount": "12000",
            "target_date": target_date.isoformat(),
            "submit": "Add Goal"
        }
    )

    assert response.status_code == 200
    assert (
        b"Current amount cannot be greater than the target amount."
        in response.data
    )


def test_past_target_date_rejected(client, app):

    create_user(
        app,
        "Past Date User",
        "pastgoaluser",
        "pastgoal@example.com"
    )

    login_user(
        client,
        "pastgoal@example.com"
    )

    past_date = date.today() - timedelta(days=1)

    response = client.post(
        "/goals/",
        data={
            "name": "Past Goal",
            "target_amount": "10000",
            "current_amount": "2000",
            "target_date": past_date.isoformat(),
            "submit": "Add Goal"
        }
    )

    assert response.status_code == 200
    assert (
        b"Target date cannot be in the past."
        in response.data
    )


def test_edit_goal_success(client, app):

    user_id = create_user(
        app,
        "Edit Goal User",
        "editgoaluser",
        "editgoal@example.com"
    )

    login_user(
        client,
        "editgoal@example.com"
    )

    original_date = date.today() + timedelta(days=30)

    with app.app_context():

        goal = Goal(
            user_id=user_id,
            name="Old Goal",
            target_amount=50000,
            current_amount=10000,
            target_date=original_date
        )

        db.session.add(goal)
        db.session.commit()

        goal_id = goal.id

    updated_date = date.today() + timedelta(days=60)

    response = client.post(
        f"/goals/edit/{goal_id}",
        data={
            "name": "Updated Goal",
            "target_amount": "75000",
            "current_amount": "25000",
            "target_date": updated_date.isoformat(),
            "submit": "Update Goal"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Savings goal updated successfully!" in response.data

    with app.app_context():

        goal = db.session.get(
            Goal,
            goal_id
        )

        assert goal.name == "Updated Goal"
        assert float(goal.target_amount) == 75000.00
        assert float(goal.current_amount) == 25000.00
        assert goal.target_date == updated_date


def test_delete_goal_success(client, app):

    user_id = create_user(
        app,
        "Delete Goal User",
        "deletegoaluser",
        "deletegoal@example.com"
    )

    login_user(
        client,
        "deletegoal@example.com"
    )

    target_date = date.today() + timedelta(days=30)

    with app.app_context():

        goal = Goal(
            user_id=user_id,
            name="Delete Goal",
            target_amount=20000,
            current_amount=5000,
            target_date=target_date
        )

        db.session.add(goal)
        db.session.commit()

        goal_id = goal.id

    response = client.post(
        f"/goals/delete/{goal_id}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Savings goal deleted successfully!" in response.data

    with app.app_context():

        goal = db.session.get(
            Goal,
            goal_id
        )

        assert goal is None


def test_user_cannot_edit_another_users_goal(
    client,
    app
):

    owner_id = create_user(
        app,
        "Goal Owner",
        "goalowner",
        "goalowner@example.com"
    )

    other_user_id = create_user(
        app,
        "Other Goal User",
        "othergoaluser",
        "othergoaluser@example.com"
    )

    target_date = date.today() + timedelta(days=30)

    with app.app_context():

        goal = Goal(
            user_id=owner_id,
            name="Private Goal",
            target_amount=50000,
            current_amount=10000,
            target_date=target_date
        )

        db.session.add(goal)
        db.session.commit()

        goal_id = goal.id

    authenticate_user(
        client,
        other_user_id
    )

    response = client.get(
        f"/goals/edit/{goal_id}"
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_goal(
    client,
    app
):

    owner_id = create_user(
        app,
        "Goal Owner Two",
        "goalowner2",
        "goalowner2@example.com"
    )

    other_user_id = create_user(
        app,
        "Other Goal User Two",
        "othergoaluser2",
        "othergoaluser2@example.com"
    )

    target_date = date.today() + timedelta(days=30)

    with app.app_context():

        goal = Goal(
            user_id=owner_id,
            name="Protected Goal",
            target_amount=50000,
            current_amount=10000,
            target_date=target_date
        )

        db.session.add(goal)
        db.session.commit()

        goal_id = goal.id

    authenticate_user(
        client,
        other_user_id
    )

    response = client.post(
        f"/goals/delete/{goal_id}"
    )

    assert response.status_code == 404

    with app.app_context():

        goal = db.session.get(
            Goal,
            goal_id
        )

        assert goal is not None