import os

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    )

    database_url = os.environ.get(
        "DATABASE_URL"
    )

    # Railway may provide a generic mysql:// URL.
    # Explicitly use PyMySQL because it is the project's
    # installed MySQL driver.
    if database_url and database_url.startswith(
        "mysql://"
    ):
        database_url = database_url.replace(
            "mysql://",
            "mysql+pymysql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Password reset email configuration
    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER"
    )

    MAIL_PORT = int(
        os.environ.get(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER"
    )