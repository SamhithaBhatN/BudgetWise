from flask import Blueprint

budgets = Blueprint(
    "budgets",
    __name__,
    url_prefix="/budgets"
)

from app.budgets import routes