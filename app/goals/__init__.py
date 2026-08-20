from flask import Blueprint

goals = Blueprint(
    "goals",
    __name__,
    url_prefix="/goals"
)

from app.goals import routes