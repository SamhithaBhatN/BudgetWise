from datetime import date

from sqlalchemy import func

from app.extensions import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.notification import Notification
from app.models.transaction import Transaction
from app.models.user import User
from app.notifications.services import generate_budget_notifications


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


def create_expense_category(
    app,
    user_id,
    name="Food"
):

    with app.app_context():

        category = Category(
            user_id=user_id,
            name=name,
            type="Expense"
        )

        db.session.add(category)
        db.session.commit()

        return category.id


def test_add_budget_success(client, app):

    user_id = create_user(
        app,
        "Budget User",
        "budgetuser",
        "budget@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "budget@example.com"
    )

    today = date.today()

    response = client.post(
        "/budgets/",
        data={
            "category_id": str(category_id),
            "amount": "10000",
            "month": str(today.month),
            "year": str(today.year),
            "submit": "Add Budget"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Budget added successfully!" in response.data

    with app.app_context():

        budget = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            month=today.month,
            year=today.year
        ).first()

        assert budget is not None
        assert float(budget.amount) == 10000.00


def test_duplicate_budget_rejected(client, app):

    user_id = create_user(
        app,
        "Duplicate Budget User",
        "duplicatebudgetuser",
        "duplicatebudget@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "duplicatebudget@example.com"
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        db.session.add(budget)
        db.session.commit()

    response = client.post(
        "/budgets/",
        data={
            "category_id": str(category_id),
            "amount": "15000",
            "month": str(today.month),
            "year": str(today.year),
            "submit": "Add Budget"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"A budget already exists for this category and month."
        in response.data
    )

    with app.app_context():

        budgets = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            month=today.month,
            year=today.year
        ).all()

        assert len(budgets) == 1
        assert float(budgets[0].amount) == 10000.00


def test_past_month_budget_rejected(client, app):

    user_id = create_user(
        app,
        "Past Budget User",
        "pastbudgetuser",
        "pastbudget@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "pastbudget@example.com"
    )

    today = date.today()

    if today.month == 1:

        past_month = 12
        past_year = today.year - 1

    else:

        past_month = today.month - 1
        past_year = today.year

    response = client.post(
        "/budgets/",
        data={
            "category_id": str(category_id),
            "amount": "5000",
            "month": str(past_month),
            "year": str(past_year),
            "submit": "Add Budget"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"You cannot create a budget for a month that has already passed."
        in response.data
    )

    with app.app_context():

        budget = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            month=past_month,
            year=past_year
        ).first()

        assert budget is None


def test_budget_progress_calculation(client, app):

    user_id = create_user(
        app,
        "Progress User",
        "progressuser",
        "progress@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "progress@example.com"
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        transaction = Transaction(
            user_id=user_id,
            title="Food Expense",
            amount=2500,
            type="Expense",
            category="Food",
            date=today,
            note="Test expense"
        )

        db.session.add(budget)
        db.session.add(transaction)
        db.session.commit()

    response = client.get(
        "/budgets/"
    )

    assert response.status_code == 200

    with app.app_context():

        budget = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            month=today.month,
            year=today.year
        ).first()

        spent = (
            db.session.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "Expense",
                Transaction.category == "Food"
            )
            .filter(
                func.extract(
                    "month",
                    Transaction.date
                ) == today.month,
                func.extract(
                    "year",
                    Transaction.date
                ) == today.year
            )
            .scalar()
        )

        assert budget is not None
        assert float(spent) == 2500.00

        percentage = (
            float(spent)
            / float(budget.amount)
        ) * 100

        assert percentage == 25.0


def test_budget_warning_generated_at_80_percent(
    client,
    app
):

    user_id = create_user(
        app,
        "Warning User",
        "warninguser",
        "warning@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "warning@example.com"
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        transaction = Transaction(
            user_id=user_id,
            title="Food Expense",
            amount=8000,
            type="Expense",
            category="Food",
            date=today
        )

        db.session.add(budget)
        db.session.add(transaction)
        db.session.commit()

        budget_id = budget.id

    response = client.get(
        "/budgets/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            budget_id=budget_id,
            type="budget_warning",
            is_read=False
        ).first()

        assert notification is not None
        assert notification.title == "Budget Warning"


def test_budget_exceeded_notification_at_100_percent(
    client,
    app
):

    user_id = create_user(
        app,
        "Exceeded User",
        "exceededuser",
        "exceeded@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    login_user(
        client,
        "exceeded@example.com"
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        transaction = Transaction(
            user_id=user_id,
            title="Food Expense",
            amount=10500,
            type="Expense",
            category="Food",
            date=today
        )

        db.session.add(budget)
        db.session.add(transaction)
        db.session.commit()

        budget_id = budget.id

    response = client.get(
        "/budgets/"
    )

    assert response.status_code == 200

    with app.app_context():

        notification = Notification.query.filter_by(
            user_id=user_id,
            budget_id=budget_id,
            type="budget_exceeded",
            is_read=False
        ).first()

        assert notification is not None
        assert notification.title == "Budget Exceeded"


def test_user_cannot_edit_another_users_budget(
    client,
    app
):

    owner_id = create_user(
        app,
        "Budget Owner",
        "budgetowner",
        "budgetowner@example.com"
    )

    other_user_id = create_user(
        app,
        "Other User",
        "otherbudgetuser",
        "otherbudgetuser@example.com"
    )

    category_id = create_expense_category(
        app,
        owner_id
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=owner_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        db.session.add(budget)
        db.session.commit()

        budget_id = budget.id

    authenticate_user(
        client,
        other_user_id
    )

    response = client.get(
        f"/budgets/edit/{budget_id}"
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_budget(
    client,
    app
):

    owner_id = create_user(
        app,
        "Budget Owner Two",
        "budgetowner2",
        "budgetowner2@example.com"
    )

    other_user_id = create_user(
        app,
        "Other User Two",
        "otherbudgetuser2",
        "otherbudgetuser2@example.com"
    )

    category_id = create_expense_category(
        app,
        owner_id
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=owner_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        db.session.add(budget)
        db.session.commit()

        budget_id = budget.id

    authenticate_user(
        client,
        other_user_id
    )

    response = client.post(
        f"/budgets/delete/{budget_id}"
    )

    assert response.status_code == 404

    with app.app_context():

        budget = db.session.get(
            Budget,
            budget_id
        )

        assert budget is not None


def test_budget_notification_service_directly(app):

    user_id = create_user(
        app,
        "Notification User",
        "notificationuser",
        "notification@example.com"
    )

    category_id = create_expense_category(
        app,
        user_id
    )

    today = date.today()

    with app.app_context():

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            amount=10000,
            month=today.month,
            year=today.year
        )

        transaction = Transaction(
            user_id=user_id,
            title="Food Expense",
            amount=8000,
            type="Expense",
            category="Food",
            date=today
        )

        db.session.add(budget)
        db.session.add(transaction)
        db.session.commit()

        budget_id = budget.id

        generate_budget_notifications(
            user_id
        )

        notification = Notification.query.filter_by(
            user_id=user_id,
            budget_id=budget_id,
            type="budget_warning",
            is_read=False
        ).first()

        assert notification is not None
        assert notification.title == "Budget Warning"