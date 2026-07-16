import os

class Config:
    SECRET_KEY = "BudgetWise@Samhitha311#2026"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:L23,us20.25@localhost/budgetwise_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False