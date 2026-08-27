from datetime import date

from app.extensions import db
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


def test_monthly_report_totals(
    client,
    app
):

    user_id = create_user(
        app,
        "Report User",
        "reportuser",
        "report@example.com"
    )

    login_user(
        client,
        "report@example.com"
    )

    with app.app_context():

        db.session.add_all([

            Transaction(
                user_id=user_id,
                title="Salary",
                amount=50000,
                type="Income",
                category="Salary",
                date=date(2026, 8, 5)
            ),

            Transaction(
                user_id=user_id,
                title="Food",
                amount=5000,
                type="Expense",
                category="Food",
                date=date(2026, 8, 10)
            ),

            Transaction(
                user_id=user_id,
                title="Transport",
                amount=2000,
                type="Expense",
                category="Transport",
                date=date(2026, 8, 15)
            ),

            Transaction(
                user_id=user_id,
                title="Old Salary",
                amount=30000,
                type="Income",
                category="Salary",
                date=date(2026, 7, 5)
            )

        ])

        db.session.commit()

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"50,000.00" in response.data
    assert b"7,000.00" in response.data
    assert b"43,000.00" in response.data


def test_monthly_report_transaction_count(
    client,
    app
):

    user_id = create_user(
        app,
        "Count User",
        "countuser",
        "count@example.com"
    )

    login_user(
        client,
        "count@example.com"
    )

    with app.app_context():

        db.session.add_all([

            Transaction(
                user_id=user_id,
                title="Salary",
                amount=40000,
                type="Income",
                category="Salary",
                date=date(2026, 8, 1)
            ),

            Transaction(
                user_id=user_id,
                title="Food",
                amount=3000,
                type="Expense",
                category="Food",
                date=date(2026, 8, 5)
            ),

            Transaction(
                user_id=user_id,
                title="Bus",
                amount=1000,
                type="Expense",
                category="Transport",
                date=date(2026, 8, 10)
            )

        ])

        db.session.commit()

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"3" in response.data


def test_category_expense_breakdown(
    client,
    app
):

    user_id = create_user(
        app,
        "Category Report User",
        "categoryreportuser",
        "categoryreport@example.com"
    )

    login_user(
        client,
        "categoryreport@example.com"
    )

    with app.app_context():

        db.session.add_all([

            Transaction(
                user_id=user_id,
                title="Lunch",
                amount=3000,
                type="Expense",
                category="Food",
                date=date(2026, 8, 3)
            ),

            Transaction(
                user_id=user_id,
                title="Dinner",
                amount=2000,
                type="Expense",
                category="Food",
                date=date(2026, 8, 8)
            ),

            Transaction(
                user_id=user_id,
                title="Bus",
                amount=1500,
                type="Expense",
                category="Transport",
                date=date(2026, 8, 12)
            )

        ])

        db.session.commit()

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Food" in response.data
    assert b"5,000.00" in response.data
    assert b"Transport" in response.data
    assert b"1,500.00" in response.data


def test_report_excludes_other_users(
    client,
    app
):

    user_id = create_user(
        app,
        "Report Owner",
        "reportowner",
        "reportowner@example.com"
    )

    other_user_id = create_user(
        app,
        "Other User",
        "otherreportuser",
        "otherreport@example.com"
    )

    login_user(
        client,
        "reportowner@example.com"
    )

    with app.app_context():

        db.session.add_all([

            Transaction(
                user_id=user_id,
                title="My Income",
                amount=30000,
                type="Income",
                category="Salary",
                date=date(2026, 8, 5)
            ),

            Transaction(
                user_id=other_user_id,
                title="Other Income",
                amount=99999,
                type="Income",
                category="Salary",
                date=date(2026, 8, 5)
            )

        ])

        db.session.commit()

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"30,000.00" in response.data
    assert b"99,999.00" not in response.data


def test_six_month_trend(
    client,
    app
):

    user_id = create_user(
        app,
        "Trend User",
        "trenduser",
        "trend@example.com"
    )

    login_user(
        client,
        "trend@example.com"
    )

    with app.app_context():

        db.session.add_all([

            Transaction(
                user_id=user_id,
                title="March Salary",
                amount=30000,
                type="Income",
                category="Salary",
                date=date(2026, 3, 5)
            ),

            Transaction(
                user_id=user_id,
                title="April Salary",
                amount=32000,
                type="Income",
                category="Salary",
                date=date(2026, 4, 5)
            ),

            Transaction(
                user_id=user_id,
                title="May Food",
                amount=4000,
                type="Expense",
                category="Food",
                date=date(2026, 5, 10)
            ),

            Transaction(
                user_id=user_id,
                title="June Food",
                amount=5000,
                type="Expense",
                category="Food",
                date=date(2026, 6, 10)
            ),

            Transaction(
                user_id=user_id,
                title="July Salary",
                amount=35000,
                type="Income",
                category="Salary",
                date=date(2026, 7, 5)
            ),

            Transaction(
                user_id=user_id,
                title="August Food",
                amount=6000,
                type="Expense",
                category="Food",
                date=date(2026, 8, 10)
            )

        ])

        db.session.commit()

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Mar 2026" in response.data
    assert b"Apr 2026" in response.data
    assert b"May 2026" in response.data
    assert b"Jun 2026" in response.data
    assert b"Jul 2026" in response.data
    assert b"Aug 2026" in response.data


def test_report_with_no_transactions(
    client,
    app
):

    create_user(
        app,
        "Empty Report User",
        "emptyreportuser",
        "emptyreport@example.com"
    )

    login_user(
        client,
        "emptyreport@example.com"
    )

    response = client.post(
        "/reports/",
        data={
            "month": "8",
            "year": "2026",
            "submit": "Generate Report"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"0.00" in response.data
    assert b"No expenses this month" in response.data