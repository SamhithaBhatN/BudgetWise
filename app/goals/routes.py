from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.goals import goals
from app.goals.forms import GoalForm
from app.models.goal import Goal
from app.extensions import db
from app.notifications.goal_services import generate_goal_notifications


@goals.route("/", methods=["GET", "POST"])
@login_required
def index():

    form = GoalForm()

    goals_list = (
        Goal.query
        .filter_by(user_id=current_user.id)
        .order_by(Goal.target_date.asc())
        .all()
    )

    # Generate or refresh goal reminder notifications
    generate_goal_notifications(current_user.id)

    if form.validate_on_submit():

        goal = Goal(
            user_id=current_user.id,
            name=form.name.data,
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data,
            target_date=form.target_date.data
        )

        db.session.add(goal)
        db.session.commit()

        flash(
            "Savings goal added successfully!",
            "success"
        )

        return redirect(
            url_for("goals.index")
        )

    return render_template(
        "goals/index.html",
        form=form,
        goals=goals_list
    )


@goals.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    form = GoalForm(obj=goal)

    if form.validate_on_submit():

        goal.name = form.name.data
        goal.target_amount = form.target_amount.data
        goal.current_amount = form.current_amount.data
        goal.target_date = form.target_date.data

        db.session.commit()

        flash(
            "Savings goal updated successfully!",
            "success"
        )

        return redirect(
            url_for("goals.index")
        )

    return render_template(
        "goals/edit_goal.html",
        form=form
    )


@goals.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@login_required
def delete_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(goal)
    db.session.commit()

    flash(
        "Savings goal deleted successfully!",
        "success"
    )

    return redirect(
        url_for("goals.index")
    )