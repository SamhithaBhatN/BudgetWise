from flask import Blueprint

categories = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories"
)

from app.categories import routes