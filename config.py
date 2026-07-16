import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-this-to-a-secure-random-key"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:L23,us20.25@localhost/budgetwise_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False