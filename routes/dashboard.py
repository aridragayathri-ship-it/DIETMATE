from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required
from flask_login import current_user
from sqlalchemy import or_
from models import Food, MealPlan, ShoppingList
from services.meal_engine import MEAL_SLOTS, build_recommendations
from services.nutrition_calculator import daily_summary
from services.water_tracker import water_summary

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
@login_required
def index():
    today = date.today()
    plan = MealPlan.query.filter_by(user_id=current_user.id, plan_date=today).first()
    slots = {"Breakfast", "Lunch", "Dinner"}
    if plan and plan.items:
        schedule_items = [{"meal_type": item.meal_type, "food": item.food, "time": item.planned_time, "servings": item.servings} for item in plan.items if item.meal_type in slots and item.food]
        schedule_items.sort(key=lambda item: item["time"])
        foods = [row["food"] for row in schedule_items[:3]]
    else:
        picks = build_recommendations(current_user, today)
        chosen = [row for row in picks if row["slot"]["name"] in slots]
        foods = [row["food"] for row in chosen[:3]]
        schedule_items = [{"meal_type": row["slot"]["name"], "food": row["food"], "time": row["slot"]["time"], "servings": 1} for row in chosen]
    nutrition = daily_summary(current_user, today)
    water = water_summary(current_user.id, today, current_user.profile.water_goal_ml if current_user.profile else 2000)
    shopping_list = ShoppingList.query.filter_by(user_id=current_user.id).order_by(ShoppingList.created_at.desc(), ShoppingList.id.desc()).first()
    shopping_items = sorted(shopping_list.items, key=lambda item: (item.purchased, item.name.casefold()))[:5] if shopping_list else []
    shopping_total = len(shopping_list.items) if shopping_list else 0
    shopping_purchased = sum(item.purchased for item in shopping_list.items) if shopping_list else 0
    return render_template("dashboard/index.html", foods=foods, schedule_items=schedule_items, today=today, plan_exists=bool(plan and plan.items), nutrition=nutrition, water=water,
                           shopping_list=shopping_list, shopping_items=shopping_items, shopping_total=shopping_total, shopping_purchased=shopping_purchased)
