from flask import Blueprint

transactions = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions"
)

from app.transactions import routes