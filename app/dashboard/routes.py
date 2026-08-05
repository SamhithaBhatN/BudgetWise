from flask import render_template
from flask_login import login_required, current_user

from app.dashboard import dashboard


@dashboard.route("/")
@login_required
def home():
    return render_template(
        "dashboard/dashboard.html",
        user=current_user
    )