# 💰 BudgetWise

> Smart Personal Finance & Expense Management System built with Python, Flask, MySQL, SQLAlchemy, Bootstrap, and pytest.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.51-red?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Tests-47%20passing-success?logo=pytest&logoColor=white)](https://pytest.org/)

BudgetWise is a full-stack web application designed to help individuals organize and manage their personal finances in one place. It provides features for tracking income and expenses, organizing transactions by category, creating monthly budgets, monitoring savings goals, receiving financial notifications, and generating monthly financial reports.

The application currently uses **INR (₹)** as its supported currency and includes secure authentication, user-specific data isolation, form validation, database migrations, and automated testing.

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Application Workflow](#-application-workflow)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Project Structure](#-project-structure)
- [Database Design](#-database-design)
- [Database Migrations](#-database-migrations)
- [Authentication & Security](#-authentication--security)
- [Validation & Business Rules](#-validation--business-rules)
- [Notifications](#-notifications)
- [Reports & Analytics](#-reports--analytics)
- [Testing](#-testing)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Useful Commands](#-useful-commands)
- [Screenshots](#-screenshots)
- [Project Status](#-project-status)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

## 📌 Overview

BudgetWise provides a centralized platform for managing everyday personal finances.

Users can:

- Create and manage an account
- Record income and expenses
- Organize transactions into categories
- Create monthly budgets
- Monitor budget utilization
- Track spending and remaining budget
- Set and monitor savings goals
- Receive budget notifications
- Receive savings-goal reminders
- View and manage notifications
- Generate monthly financial reports
- Analyze category-wise expenses
- View six-month income and expense trends
- Manage profile information
- Change account passwords
- Manage notification preferences

The application is currently focused on **INR-based personal finance management**.

---

## ✨ Key Features

### 🔐 Authentication

BudgetWise uses Flask-Login for session-based authentication.

- User registration
- Duplicate username validation
- Duplicate email validation
- Secure password hashing
- Login and logout
- Protected routes
- User-specific data access

Passwords are stored as secure hashes rather than plain-text passwords.

### 💳 Transaction Management

The transaction module supports:

- Add income transactions
- Add expense transactions
- Select transaction categories
- Enter transaction title and amount
- Add transaction notes
- Select transaction date
- Edit transactions
- Delete transactions
- Transaction validation
- User ownership protection

Transactions are classified as:

```text
Income
Expense
```

### 🗂️ Category Management

Categories organize transactions for easier tracking and reporting.

- Create income categories
- Create expense categories
- View categories
- Edit categories
- Delete categories
- User-specific category ownership

### 📊 Budget Management

BudgetWise supports monthly budgets by expense category.

Users can:

- Create monthly budgets
- Select a spending category
- Define a budget amount
- Track spending
- View budget utilization
- View remaining budget
- Edit budgets
- Delete budgets

#### Budget Rules

- Duplicate budgets for the same category and month are rejected.
- Budgets for past months are rejected.
- Budget amounts must be valid.
- Spending is based on matching expense transactions.
- Users can only manage their own budgets.

#### Budget Notifications

```text
Below 80%       → No active budget warning
80% - 99.99%    → Budget Warning
100% or more    → Budget Exceeded
```

### 🎯 Savings Goals

Users can create savings goals and monitor progress toward financial targets.

- Create goals
- Set target amounts
- Set current saved amounts
- Set target dates
- Track progress
- Edit goals
- Delete goals

#### Goal Rules

- Current savings cannot exceed the target amount.
- Target dates cannot be in the past.
- Completed goals do not continue generating reminders.
- Users can only manage their own goals.

### 🔔 Notifications

BudgetWise provides notifications for important financial events.

Supported notification types include:

```text
budget_warning
budget_exceeded
goal_reminder
```

Users can:

- View notifications
- Mark notifications as read
- See unread notification counts
- Access only their own notifications

#### Goal Reminder Window

```text
7 days or less remaining → Goal Reminder
1 day remaining           → Due tomorrow
0 days remaining          → Due today
More than 7 days          → No reminder
Completed goal            → No reminder
```

Budget alerts and goal reminders respect user notification settings.

### 📈 Reports & Analytics

The reports module provides:

- Monthly income totals
- Monthly expense totals
- Net balance
- Transaction count
- Category-wise expense breakdown
- Six-month income trend
- Six-month expense trend
- Reports for months with no transactions

Net balance is calculated as:

```text
Net Balance = Total Income - Total Expenses
```

The six-month trend includes the selected month and the five preceding months.

---

## 🔄 Application Workflow

```text
                         ┌───────────────────┐
                         │   Landing Page    │
                         └─────────┬─────────┘
                                   │
                          ┌────────▼────────┐
                          │ Register / Login│
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │    Dashboard    │
                          └────────┬────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    Transactions              Budgets                   Goals
          │                        │                        │
          └────────────────┬───────┴────────┬───────────────┘
                           │                │
                           ▼                ▼
                    Notifications        Reports
                           │
                           ▼
                    Profile / Settings
```

---

## 🛠️ Tech Stack

### Backend

- Python 3.11
- Flask 3.1.3
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.51
- Flask-Migrate 4.1.0
- Alembic 1.18.5
- Flask-WTF 1.3.0
- WTForms 3.2.2
- bcrypt 5.0.0
- PyMySQL 1.2.0
- python-dotenv 1.2.2

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Bootstrap Icons
- Google Fonts

### Database

- MySQL

### Testing

- pytest 9.1.1

---

## 🏗️ Project Architecture

BudgetWise follows a modular Flask architecture based on the application factory pattern.

The application uses:

- Flask application factory
- Feature-based blueprints
- SQLAlchemy ORM
- Flask-Migrate and Alembic
- Flask-Login authentication
- Flask-WTF forms
- Jinja2 templates
- Notification service modules
- Static CSS and JavaScript
- Dedicated automated tests

### Application Factory

The Flask application is created through:

```python
create_app()
```

The factory is responsible for:

- Creating the Flask application
- Loading configuration
- Initializing extensions
- Loading the authentication user loader
- Registering blueprints
- Registering context processors
- Registering error handlers

---

## 📁 Project Structure

```text
BudgetWise/
│
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── budgets/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── categories/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── goals/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── budget.py
│   │   ├── category.py
│   │   ├── goal.py
│   │   ├── notification.py
│   │   ├── transaction.py
│   │   ├── user.py
│   │   └── user_settings.py
│   │
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   ├── goal_services.py
│   │   ├── routes.py
│   │   ├── services.py
│   │   └── utils.py
│   │
│   ├── profile/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── transactions/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── budgets/
│   │   ├── categories/
│   │   ├── components/
│   │   ├── dashboard/
│   │   ├── errors/
│   │   ├── goals/
│   │   ├── notifications/
│   │   ├── profile/
│   │   ├── reports/
│   │   ├── transactions/
│   │   ├── base.html
│   │   └── index.html
│   │
│   ├── __init__.py
│   ├── auth_loader.py
│   └── extensions.py
│
├── migrations/
│   ├── versions/
│   │   ├── 1d1ff9ea6cd3_create_users_table.py
│   │   ├── 052833ad1749_create_transactions_table.py
│   │   ├── a8add9b118b5_create_categories_table.py
│   │   ├── dadeb932ac2d_create_budgets_table.py
│   │   ├── abfd6086d11f_create_goals_table.py
│   │   ├── 77c225c206fe_create_notifications_table.py
│   │   ├── d015b7666886_link_notifications_to_budgets.py
│   │   ├── 79897c5fc4bc_create_user_settings_table.py
│   │   ├── d2813be3ac0b_link_notifications_to_goals.py
│   │   └── 567d1ca8db1f_use_inr_and_decimal_transaction_amounts.py
│   │
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── screenshots/
│   ├── landing-page.png
│   ├── dashboard.png
│   ├── transactions.png
│   ├── budgets.png
│   ├── savings-goals.png
│   └── reports.png
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_budgets.py
│   ├── test_goals.py
│   ├── test_notifications.py
│   ├── test_reports.py
│   └── test_transactions.py
│
├── .gitignore
├── CHANGELOG.md
├── config.py
├── requirements.txt
├── migrate.bat
├── run.bat
├── run.py
└── upgrade.bat
```

---

## 🗄️ Database Design

BudgetWise uses MySQL through SQLAlchemy ORM.

The current database contains:

```text
users
transactions
categories
budgets
goals
notifications
user_settings
alembic_version
```

### Main Relationships

```text
User
 │
 ├── Transactions
 │
 ├── Categories
 │
 ├── Budgets
 │
 ├── Goals
 │
 ├── Notifications
 │
 └── User Settings
```

User ownership is applied throughout the application so that users cannot access or modify another user's financial records.

---

## 🔄 Database Migrations

BudgetWise uses Flask-Migrate with Alembic for database schema management.

The migration history follows this progression:

```text
<base>
   ↓
1d1ff9ea6cd3
Create users table
   ↓
052833ad1749
Create transactions table
   ↓
a8add9b118b5
Create categories table
   ↓
dadeb932ac2d
Create budgets table
   ↓
abfd6086d11f
Create goals table
   ↓
77c225c206fe
Create notifications table
   ↓
d015b7666886
Link notifications to budgets
   ↓
79897c5fc4bc
Create user settings table
   ↓
d2813be3ac0b
Link notifications to goals
   ↓
567d1ca8db1f
Use INR and decimal transaction amounts
   ↓
HEAD
```

### Check Current Migration

```powershell
python -m flask --app run.py db current
```

### Apply Pending Migrations

```powershell
python -m flask --app run.py db upgrade
```

### View Migration History

```powershell
python -m flask --app run.py db history
```

### Generate a New Migration

After an intentional SQLAlchemy model change:

```powershell
python -m flask --app run.py db migrate -m "Describe the schema change"
```

Review the generated migration before applying it.

Then:

```powershell
python -m flask --app run.py db upgrade
```

---

## 🔐 Authentication & Security

BudgetWise includes several application-level security practices.

### Environment-Based Configuration

Sensitive configuration is loaded from environment variables:

```text
SECRET_KEY
DATABASE_URL
FLASK_DEBUG
```

The `.env` file is excluded from version control through `.gitignore`.

### Password Security

User passwords are stored as secure password hashes rather than plain-text passwords.

### Session Authentication

Flask-Login manages:

- Login sessions
- Logout
- Current user access
- User loading
- Protected routes

Authenticated routes use:

```python
@login_required
```

### CSRF Protection

Flask-WTF forms provide CSRF protection for form submissions.

### User Data Isolation

Database queries are scoped to the authenticated user.

Example:

```python
.filter_by(
    user_id=current_user.id
)
```

Edit and delete operations also validate ownership.

### Debug Configuration

Debug mode is controlled through:

```text
FLASK_DEBUG
```

Local development:

```text
FLASK_DEBUG=1
```

Production:

```text
FLASK_DEBUG=0
```

The application defaults to debug mode being disabled when the environment variable is not set.

### Migration Credential Protection

Alembic renders the configured database URL with the database password hidden.

---

## ✅ Validation & Business Rules

BudgetWise includes validation through Flask-WTF forms and application logic.

### Authentication

- Username is required
- Email is required
- Password is required
- Password confirmation must match
- Duplicate usernames are rejected
- Duplicate emails are rejected

### Transactions

- Transaction category must be valid
- Future transaction dates are rejected
- Transaction amounts must be valid

### Budgets

- Duplicate monthly budgets are rejected
- Past-month budgets are rejected
- Budget amounts must be valid

### Savings Goals

- Target amount must be valid
- Current amount cannot exceed target amount
- Target date cannot be in the past

### Ownership

Users cannot access, edit, or delete financial records belonging to another user.

---

## 🔔 Notifications

Notifications are generated through dedicated service modules.

The notification system consists of:

```text
Notification Routes
        │
        ├── View notifications
        │
        └── Mark notifications as read

Notification Services
        │
        ├── Budget notifications
        │
        └── Goal reminders
```

Budget notifications are handled through:

```text
app/notifications/services.py
```

Goal reminders are handled through:

```text
app/notifications/goal_services.py
```

Both systems respect the user's notification preferences.

When a budget or savings goal is deleted, its associated notifications are also removed to prevent orphaned notifications.

---

## 📈 Reports & Analytics

The reports module is implemented under:

```text
app/reports/
```

It supports:

- Monthly totals
- Transaction count
- Category-wise expense breakdown
- Net balance
- Six-month income trend
- Six-month expense trend
- Reports with no transactions

Reports are restricted to the authenticated user's transactions.

---

## 🧪 Testing

BudgetWise includes an automated pytest suite covering core application functionality.

### Test Modules

#### Authentication

```text
tests/test_auth.py
```

Covers:

- Registration
- Duplicate username
- Duplicate email
- Successful login
- Invalid password
- Logout

#### Budgets

```text
tests/test_budgets.py
```

Covers:

- Budget creation
- Duplicate budgets
- Past-month validation
- Budget progress
- Budget warning notifications
- Budget exceeded notifications
- Ownership protection
- Notification service behavior
- Notification cleanup when deleting budgets

#### Goals

```text
tests/test_goals.py
```

Covers:

- Goal creation
- Amount validation
- Date validation
- Goal editing
- Goal deletion
- Ownership protection
- Notification cleanup when deleting goals

#### Notifications

```text
tests/test_notifications.py
```

Covers:

- Notification page authentication
- Notification display
- Marking notifications as read
- Notification ownership
- Goal reminders
- Reminder timing
- Completed goals
- Disabled reminders
- Old reminder cleanup

#### Reports

```text
tests/test_reports.py
```

Covers:

- Monthly totals
- Transaction counts
- Category expense breakdown
- User isolation
- Six-month trends
- Empty reports

#### Transactions

```text
tests/test_transactions.py
```

Covers:

- Transaction creation
- Invalid categories
- Future dates
- Editing
- Deletion
- Ownership protection

### Run the Complete Test Suite

```powershell
pytest -v
```

### Current Test Result

```text
47 / 47 tests passing
```

The test suite uses an isolated test database configuration.

---

## ⚙️ Installation

### Requirements

Before installing BudgetWise, make sure you have:

- Python 3.11 or compatible Python 3.x
- MySQL Server
- Git
- Windows PowerShell or another terminal

### 1. Clone the Repository

```powershell
git clone https://github.com/SamhithaBhatN/BudgetWise.git
cd BudgetWise
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔐 Configuration

BudgetWise uses environment variables for sensitive configuration.

Create a `.env` file in the project root:

```text
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/budgetwise_db
FLASK_DEBUG=1
```

### Security Notes

- Do not commit `.env` to Git.
- Keep production secrets outside source code.
- Use a strong random `SECRET_KEY`.
- Use a dedicated MySQL user for production.
- Avoid using the MySQL `root` account for production application access.
- Set `FLASK_DEBUG=0` in production.

The repository already excludes `.env` through `.gitignore`.

---

## 🗃️ Database Setup

### 1. Create the Database

In MySQL:

```sql
CREATE DATABASE budgetwise_db;
```

### 2. Configure the Database Connection

In `.env`:

```text
DATABASE_URL=mysql+pymysql://username:password@localhost/budgetwise_db
```

### 3. Apply Migrations

```powershell
python -m flask --app run.py db upgrade
```

### 4. Verify Migration State

```powershell
python -m flask --app run.py db current
```

---

## ▶️ Running the Application

Start the Flask development server:

```powershell
python run.py
```

The application is normally available at:

```text
http://127.0.0.1:5000
```

---

## 🧰 Useful Commands

### Start the Application

```powershell
python run.py
```

### Run All Tests

```powershell
pytest -v
```

### Check Migration State

```powershell
python -m flask --app run.py db current
```

### Apply Migrations

```powershell
python -m flask --app run.py db upgrade
```

### View Migration History

```powershell
python -m flask --app run.py db history
```

### Generate a Migration

```powershell
python -m flask --app run.py db migrate -m "Describe the schema change"
```

### Check Git Status

```powershell
git status
```

### View Recent Commits

```powershell
git log -5 --oneline
```

---

## 📸 Screenshots

### Landing Page

![BudgetWise Landing Page](screenshots/landing-page.png)

### Dashboard

![BudgetWise Dashboard](screenshots/dashboard.png)

### Transactions

![BudgetWise Transactions](screenshots/transactions.png)

### Budgets

![BudgetWise Budgets](screenshots/budgets.png)

### Savings Goals

![BudgetWise Savings Goals](screenshots/savings-goals.png)

### Reports

![BudgetWise Reports](screenshots/reports.png)

---

## 📋 Project Status

BudgetWise is a functional full-stack personal finance management application.

Current functionality:

```text
✅ User authentication
✅ Secure password hashing
✅ Transaction management
✅ Category management
✅ Monthly budgets
✅ Budget progress tracking
✅ Budget warning notifications
✅ Budget exceeded notifications
✅ Savings goals
✅ Goal reminders
✅ Notification management
✅ Notification cleanup on budget deletion
✅ Notification cleanup on goal deletion
✅ Monthly financial reports
✅ Category-wise expense analysis
✅ Six-month financial trends
✅ Profile management
✅ Account settings
✅ MySQL database
✅ Flask-Migrate / Alembic migrations
✅ Responsive Bootstrap interface
✅ User data isolation
✅ CSRF protection
✅ Automated tests
```

### Automated Test Status

```text
47 / 47 tests passing
```

---

## 🚀 Future Enhancements

Potential future improvements include:

- Additional currency support
- Recurring transactions
- Transaction search and filtering
- CSV export
- PDF reports
- Advanced dashboard charts
- More detailed financial analytics
- Scheduled notifications
- Automated database backups
- REST API support
- Production deployment
- Improved mobile experience
- Dark mode
- More customizable categories
- Personalized financial summaries

---

## 👩‍💻 Author

### Samhitha Bhat

BudgetWise is a full-stack personal finance management project built using:

- Python
- Flask
- MySQL
- SQLAlchemy
- Bootstrap
- pytest

Repository:

https://github.com/SamhithaBhatN/BudgetWise

---

## 📄 License

This project currently does not specify an open-source license.