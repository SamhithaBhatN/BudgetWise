from app.extensions import db, login_manager

from app.models.user import User


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )