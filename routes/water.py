"""Configurable water goal, persistent intake, and weekly water history."""
from datetime import date, datetime
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from models import WaterLog
from services.water_tracker import water_summary, weekly_totals

water_bp = Blueprint("water", __name__, url_prefix="/water")


def parse_day(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


def goal_for_user():
    return current_user.profile.water_goal_ml if current_user.profile else 2000


def today_summary(day=None):
    day = day or date.today()
    return water_summary(current_user.id, day, goal_for_user())


@water_bp.get("/")
@login_required
def index():
    selected = parse_day(request.args.get("date"))
    summary = today_summary(selected)
    week = weekly_totals(current_user.id, selected)
    return render_template("water/index.html", selected=selected, summary=summary, week=week,
                           week_labels=[row["date"].strftime("%a") for row in week],
                           week_values=[row["amount_ml"] for row in week], default_time=datetime.utcnow().strftime("%H:%M"))


@water_bp.post("/add")
@login_required
def add():
    payload = request.get_json(silent=True) if request.is_json else request.form
    day = parse_day(payload.get("date") if payload else None)
    try:
        amount = int(payload.get("amount_ml", 250))
        if not 50 <= amount <= 2000:
            raise ValueError
        raw_time = payload.get("logged_time", "")
        intake_time = datetime.strptime(raw_time, "%H:%M").time() if raw_time else datetime.utcnow().time()
        db.session.add(WaterLog(user_id=current_user.id, amount_ml=amount, logged_at=datetime.combine(day, intake_time)))
        db.session.commit()
    except (ValueError, TypeError):
        db.session.rollback()
        if request.is_json:
            return jsonify(error="Enter an amount from 50 to 2,000 ml."), 400
        flash("Water amount must be between 50 and 2,000 ml.", "error")
        return redirect(url_for("water.index", date=day.isoformat()))
    summary = water_summary(current_user.id, day, goal_for_user())
    if request.is_json:
        summary.pop("logs", None)
        return jsonify(summary)
    flash(f"{amount} ml water intake recorded.", "success")
    return redirect(url_for("water.index", date=day.isoformat()))


@water_bp.post("/reset")
@login_required
def reset():
    payload = request.get_json(silent=True) if request.is_json else request.form
    day = parse_day(payload.get("date") if payload else None)
    db.session.add(WaterLog(user_id=current_user.id, amount_ml=0, logged_at=datetime.utcnow() if day == date.today() else datetime.combine(day, datetime.utcnow().time())))
    db.session.commit()
    summary = water_summary(current_user.id, day, goal_for_user())
    if request.is_json:
        summary.pop("logs", None)
        return jsonify(summary)
    flash("Today's progress was reset. Your intake history is preserved.", "success")
    return redirect(url_for("water.index", date=day.isoformat()))


@water_bp.post("/goal")
@login_required
def update_goal():
    try:
        goal = int(request.form.get("goal_ml", ""))
        if not 250 <= goal <= 10000:
            raise ValueError
        current_user.profile.water_goal_ml = goal
        db.session.commit()
        flash("Daily water goal updated.", "success")
    except (TypeError, ValueError):
        flash("Choose a daily water goal between 250 and 10,000 ml.", "error")
    return redirect(url_for("water.index"))
