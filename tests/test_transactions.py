from datetime import date, timedelta

from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction
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


def login_user(client, email, password="TestPassword123"):

    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "submit": "Login"
        },
        follow_redirects=True
    )


def create_category(
    app,
    user_id,
    name="Food",
    category_type="Expense"
):
    with app.app_context():

        category = Category(
            user_id=user_id,
            name=name,
            type=category_type
        )

        db.session.add(category)
        db.session.commit()

        return category.id


def test_add_transaction_success(client, app):

    user_id = create_user(
        app,
        "Transaction User",
        "transactionuser",
        "transaction@example.com"
    )

    create_category(
        app,
        user_id
    )

    login_response = login_user(
        client,
        "transaction@example.com"
    )

    assert login_response.status_code == 200

    response = client.post(
        "/transactions/add",
        data={
            "title": "Lunch",
            "amount": "250.50",
            "type": "Expense",
            "category": "Food",
            "date": date.today().isoformat(),
            "note": "College lunch",
            "submit": "Save Transaction"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Transaction added successfully!" in response.data

    with app.app_context():

        transaction = Transaction.query.filter_by(
            user_id=user_id,
            title="Lunch"
        ).first()

        assert transaction is not None
        assert float(transaction.amount) == 250.50
        assert transaction.type == "Expense"
        assert transaction.category == "Food"
        assert transaction.note == "College lunch"


def test_add_transaction_invalid_category(client, app):

    user_id = create_user(
        app,
        "Invalid Category User",
        "invalidcategoryuser",
        "invalidcategory@example.com"
    )

    create_category(
        app,
        user_id,
        name="Salary",
        category_type="Income"
    )

    login_user(
        client,
        "invalidcategory@example.com"
    )

    response = client.post(
        "/transactions/add",
        data={
            "title": "Invalid Expense",
            "amount": "500",
            "type": "Expense",
            "category": "Salary",
            "date": date.today().isoformat(),
            "note": "",
            "submit": "Save Transaction"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert (
        b"Invalid category selected for this transaction type."
        in response.data
    )


def test_future_transaction_date_rejected(client, app):

    user_id = create_user(
        app,
        "Future Date User",
        "futuredateuser",
        "futuredate@example.com"
    )

    create_category(
        app,
        user_id
    )

    login_user(
        client,
        "futuredate@example.com"
    )

    future_date = (
        date.today() + timedelta(days=1)
    )

    response = client.post(
        "/transactions/add",
        data={
            "title": "Future Expense",
            "amount": "500",
            "type": "Expense",
            "category": "Food",
            "date": future_date.isoformat(),
            "note": "",
            "submit": "Save Transaction"
        }
    )

    assert response.status_code == 200
    assert (
        b"Transaction date cannot be in the future."
        in response.data
    )

    with app.app_context():

        transaction = Transaction.query.filter_by(
            user_id=user_id,
            title="Future Expense"
        ).first()

        assert transaction is None


def test_edit_transaction_success(client, app):

    user_id = create_user(
        app,
        "Edit Transaction User",
        "edittransactionuser",
        "edittransaction@example.com"
    )

    create_category(
        app,
        user_id
    )

    with app.app_context():

        transaction = Transaction(
            user_id=user_id,
            title="Old Title",
            amount=100,
            type="Expense",
            category="Food",
            date=date.today(),
            note="Old note"
        )

        db.session.add(transaction)
        db.session.commit()

        transaction_id = transaction.id

    login_user(
        client,
        "edittransaction@example.com"
    )

    response = client.post(
        f"/transactions/edit/{transaction_id}",
        data={
            "title": "Updated Lunch",
            "amount": "350.75",
            "type": "Expense",
            "category": "Food",
            "date": date.today().isoformat(),
            "note": "Updated note",
            "submit": "Update Transaction"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Transaction updated successfully!" in response.data

    with app.app_context():

        transaction = db.session.get(
            Transaction,
            transaction_id
        )

        assert transaction.title == "Updated Lunch"
        assert float(transaction.amount) == 350.75
        assert transaction.note == "Updated note"


def test_delete_transaction_success(client, app):

    user_id = create_user(
        app,
        "Delete Transaction User",
        "deletetransactionuser",
        "deletetransaction@example.com"
    )

    create_category(
        app,
        user_id
    )

    with app.app_context():

        transaction = Transaction(
            user_id=user_id,
            title="Delete Me",
            amount=200,
            type="Expense",
            category="Food",
            date=date.today()
        )

        db.session.add(transaction)
        db.session.commit()

        transaction_id = transaction.id

    login_user(
        client,
        "deletetransaction@example.com"
    )

    response = client.post(
        f"/transactions/delete/{transaction_id}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Transaction deleted successfully!" in response.data

    with app.app_context():

        transaction = db.session.get(
            Transaction,
            transaction_id
        )

        assert transaction is None


def test_user_cannot_edit_another_users_transaction(
    client,
    app
):

    user_one_id = create_user(
        app,
        "User One",
        "userone",
        "userone@example.com"
    )

    user_two_id = create_user(
        app,
        "User Two",
        "usertwo",
        "usertwo@example.com"
    )

    create_category(
        app,
        user_one_id
    )

    with app.app_context():

        transaction = Transaction(
            user_id=user_one_id,
            title="Private Transaction",
            amount=500,
            type="Expense",
            category="Food",
            date=date.today()
        )

        db.session.add(transaction)
        db.session.commit()

        transaction_id = transaction.id

    login_user(
        client,
        "usertwo@example.com"
    )

    response = client.get(
        f"/transactions/edit/{transaction_id}"
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_transaction(
    client,
    app
):

    user_one_id = create_user(
        app,
        "User One",
        "userone2",
        "userone2@example.com"
    )

    create_user(
        app,
        "User Two",
        "usertwo2",
        "usertwo2@example.com"
    )

    create_category(
        app,
        user_one_id
    )

    with app.app_context():

        transaction = Transaction(
            user_id=user_one_id,
            title="Protected Transaction",
            amount=750,
            type="Expense",
            category="Food",
            date=date.today()
        )

        db.session.add(transaction)
        db.session.commit()

        transaction_id = transaction.id

    login_user(
        client,
        "usertwo2@example.com"
    )

    response = client.post(
        f"/transactions/delete/{transaction_id}"
    )

    assert response.status_code == 404

    with app.app_context():

        transaction = db.session.get(
            Transaction,
            transaction_id
        )

        assert transaction is not None