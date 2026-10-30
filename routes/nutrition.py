"""Food logging, nutrition history, weekly chart data and CSV export."""
import csv
from datetime import date, datetime
from io import StringIO
from flask import Blueprint, Response, abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from extensions import db
from models import DailyFoodLog, Food
from services.meal_engine import suitable_foods
from services.nutrition_calculator import daily_summary, logs_for_day, totals_for_logs

nutrition_bp = Blueprint("nutrition", __name__, url_prefix="/nutrition")


def parse_day(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date.today()


def owned_food(food_id):
    food = Food.query.filter(Food.id == food_id, or_(Food.owner_id.is_(None), Food.owner_id == current_user.id)).first()
    if food is None:
        abort(404)
    return food


@nutrition_bp.get("/")
@login_required
def index():
    selected = parse_day(request.args.get("date"))
    summary = daily_summary(current_user, selected)
    foods = suitable_foods(current_user)
    week = []
    for offset in range(6, -1, -1):
        day = selected.fromordinal(selected.toordinal() - offset)
        logs = summary["logs"] if day == selected else logs_for_day(current_user.id, day)
        week.append({"date": day, "calories": totals_for_logs(logs)["calories"]})
    return render_template("nutrition/index.html", selected=selected, summary=summary, foods=foods, week=week,
                          week_labels=[entry["date"].strftime("%a") for entry in week], week_values=[entry["calories"] for entry in week],
                          default_time=datetime.utcnow().strftime("%H:%M"))


@nutrition_bp.post("/log")
@login_required
def log_food():
    selected = parse_day(request.form.get("date"))
    try:
        food_id = int(request.form.get("food_id", ""))
        servings = float(request.form.get("servings", "1"))
        if not 0.1 <= servings <= 20:
            raise ValueError
        food = owned_food(food_id)
        allowed_ids = {item.id for item in suitable_foods(current_user)}
        if food.id not in allowed_ids:
            raise ValueError("This food does not match your current dietary preference or restrictions.")
        raw_time = request.form.get("logged_time", "")
        chosen_time = datetime.strptime(raw_time, "%H:%M").time() if raw_time else datetime.utcnow().time()
        db.session.add(DailyFoodLog(user_id=current_user.id, food_id=food.id, servings=servings, logged_at=datetime.combine(selected, chosen_time)))
        db.session.commit()
        flash(f"{food.name} added to your food log.", "success")
    except ValueError:
        db.session.rollback()
        flash("Choose an available food, a valid time, and 0.1–20 servings.", "error")
    return redirect(url_for("nutrition.index", date=selected.isoformat()))


@nutrition_bp.post("/delete/<int:log_id>")
@login_required
def delete_log(log_id):
    log = DailyFoodLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    selected = log.logged_at.date()
    db.session.delete(log)
    db.session.commit()
    flash("Food log entry removed.", "success")
    return redirect(url_for("nutrition.index", date=selected.isoformat()))


@nutrition_bp.get("/export.csv")
@login_required
def export_csv():
    selected = parse_day(request.args.get("date"))
    logs = daily_summary(current_user, selected)["logs"]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Date", "Time", "Food", "Servings", "Calories (kcal)", "Protein (g)", "Carbohydrates (g)", "Fat (g)"])
    for log in logs:
        food = log.food
        if not food:
            continue
        writer.writerow([selected.isoformat(), log.logged_at.strftime("%H:%M"), food.name, log.servings, round(food.calories * log.servings, 1), round(food.protein_g * log.servings, 1), round(food.carbs_g * log.servings, 1), round(food.fat_g * log.servings, 1)])
    response = make_response(stream.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=dietmate-nutrition-{selected.isoformat()}.csv"
    return response
