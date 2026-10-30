"""Adaptive plan generation and meal schedule CRUD."""
from datetime import date, datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from extensions import db
from models import Food, MealItem, MealPlan
from services.meal_engine import MEAL_SLOTS, build_recommendations, calorie_target, recommendation_for_slot, suitable_foods

meal_bp = Blueprint("meal", __name__, url_prefix="/planner")
SLOT_NAMES = {slot["name"] for slot in MEAL_SLOTS}


def parse_plan_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


def owned_plan(plan_id):
    plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if plan is None:
        abort(404)
    return plan


def get_or_create_plan(plan_date):
    plan = MealPlan.query.filter_by(user_id=current_user.id, plan_date=plan_date).first()
    if plan is None:
        plan = MealPlan(user_id=current_user.id, plan_date=plan_date)
        db.session.add(plan)
        db.session.flush()
    return plan


def validate_schedule():
    slot = request.form.get("meal_type", "")
    planned_time = request.form.get("planned_time", "")
    try:
        servings = float(request.form.get("servings", "1"))
        datetime.strptime(planned_time, "%H:%M")
    except (ValueError, TypeError):
        raise ValueError("Enter a valid planned time and serving quantity.")
    if slot not in SLOT_NAMES or not 0.25 <= servings <= 10:
        raise ValueError("Choose a meal category and a serving quantity between 0.25 and 10.")
    try:
        food_id = int(request.form.get("food_id", ""))
    except ValueError:
        raise ValueError("Choose a food from your available foods.")
    eligible = {food.id for food in suitable_foods(current_user)}
    if food_id not in eligible:
        raise ValueError("That food is not available for your dietary preferences or restrictions.")
    return slot, planned_time, servings, Food.query.get(food_id)


@meal_bp.get("/")
@login_required
def index():
    plan_date = parse_plan_date(request.args.get("date"))
    plan = MealPlan.query.filter_by(user_id=current_user.id, plan_date=plan_date).first()
    target, measured = calorie_target(current_user.profile)
    foods = suitable_foods(current_user)
    previews = [] if plan and plan.items else build_recommendations(current_user, plan_date)
    rows = [{"slot": item.meal_type, "time": item.planned_time, "servings": item.servings, "food": item.food, "reason": item.recommendation_reason, "item": item} for item in sorted(plan.items, key=lambda meal: meal.planned_time)] if plan else []
    total_calories = sum((row["food"].calories * row["servings"] for row in rows if row["food"]), 0)
    total_prep = sum(row["food"].preparation_minutes for row in rows if row["food"])
    return render_template("meals/planner.html", plan=plan, plan_date=plan_date, target=target, measured=measured, foods=foods, slots=MEAL_SLOTS, previews=previews, rows=rows, total_calories=round(total_calories), total_prep=total_prep)


@meal_bp.post("/generate")
@login_required
def generate():
    plan_date = parse_plan_date(request.form.get("date"))
    recommendations = build_recommendations(current_user, plan_date)
    if not recommendations:
        flash(recommendations[0]["reason"] if recommendations else "No matching foods are available.", "error")
        return redirect(url_for("meal.index", date=plan_date.isoformat()))
    try:
        plan = get_or_create_plan(plan_date)
        plan.items.clear()
        for recommendation in recommendations:
            plan.items.append(MealItem(food=recommendation["food"], meal_type=recommendation["slot"]["name"], planned_time=recommendation["slot"]["time"], servings=1, recommendation_reason=recommendation["reason"]))
        db.session.commit()
        flash("Your personalized meal plan is ready.", "success")
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for("meal.index", date=plan_date.isoformat()))


@meal_bp.post("/<int:plan_id>/regenerate/<int:item_id>")
@login_required
def regenerate_item(plan_id, item_id):
    plan = owned_plan(plan_id)
    item = next((row for row in plan.items if row.id == item_id), None)
    if item is None:
        abort(404)
    slot = next((slot for slot in MEAL_SLOTS if slot["name"] == item.meal_type), None)
    if slot is None:
        abort(400)
    excluded = {row.food_id for row in plan.items if row.id != item.id and row.food_id}
    food, reason = recommendation_for_slot(current_user, slot, excluded, plan.plan_date)
    if food is None:
        flash(reason, "error")
    else:
        item.food, item.recommendation_reason = food, reason
        db.session.commit()
        flash(f"{item.meal_type} recommendation refreshed.", "success")
    return redirect(url_for("meal.index", date=plan.plan_date.isoformat()))


@meal_bp.post("/<int:plan_id>/add")
@login_required
def add_item(plan_id):
    plan = owned_plan(plan_id)
    try:
        slot, planned_time, servings, food = validate_schedule()
        plan.items.append(MealItem(food=food, meal_type=slot, planned_time=planned_time, servings=servings))
        db.session.commit()
        flash("Meal added to your plan.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("meal.index", date=plan.plan_date.isoformat()))


@meal_bp.post("/<int:plan_id>/edit/<int:item_id>")
@login_required
def edit_item(plan_id, item_id):
    plan = owned_plan(plan_id)
    item = next((row for row in plan.items if row.id == item_id), None)
    if item is None:
        abort(404)
    try:
        slot, planned_time, servings, food = validate_schedule()
        item.meal_type, item.planned_time, item.servings, item.food = slot, planned_time, servings, food
        item.recommendation_reason = ""
        db.session.commit()
        flash("Meal schedule updated.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("meal.index", date=plan.plan_date.isoformat()))


@meal_bp.post("/<int:plan_id>/delete/<int:item_id>")
@login_required
def delete_item(plan_id, item_id):
    plan = owned_plan(plan_id)
    item = next((row for row in plan.items if row.id == item_id), None)
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash("Meal removed from your plan.", "success")
    return redirect(url_for("meal.index", date=plan.plan_date.isoformat()))
