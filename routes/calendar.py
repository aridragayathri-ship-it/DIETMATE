"""Month/week calendar views and private plan copying."""
import calendar as pycalendar
from datetime import date, datetime, timedelta
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from models import MealItem, MealPlan

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


@calendar_bp.get("/")
@login_required
def index():
    selected = parse_date(request.args.get("date"))
    view = "week" if request.args.get("view") == "week" else "month"
    if view == "week":
        start = selected - timedelta(days=selected.weekday())
        dates = [start + timedelta(days=offset) for offset in range(7)]
    else:
        start = selected.replace(day=1)
        calendar = pycalendar.Calendar(firstweekday=0)
        dates = list(calendar.itermonthdates(selected.year, selected.month))
    end = dates[-1]
    plans = MealPlan.query.filter(MealPlan.user_id == current_user.id, MealPlan.plan_date >= dates[0], MealPlan.plan_date <= end).all()
    by_date = {plan.plan_date: plan for plan in plans}
    days = [{"date": day, "in_month": day.month == selected.month, "selected": day == selected, "plan": by_date.get(day)} for day in dates]
    prev = (selected - timedelta(days=7)) if view == "week" else (selected.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_day = (selected + timedelta(days=7)) if view == "week" else ((selected.replace(day=28) + timedelta(days=4)).replace(day=1))
    return render_template("calendar/index.html", selected=selected, view=view, days=days, previous=prev, next_date=next_day,
                           today=date.today().isoformat(), month_name=selected.strftime("%B %Y"), week_start=dates[0], week_end=dates[-1], weekdays=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])


@calendar_bp.post("/copy")
@login_required
def copy_plan():
    source_date = parse_date(request.form.get("source_date"))
    target_date = parse_date(request.form.get("target_date"))
    source = MealPlan.query.filter_by(user_id=current_user.id, plan_date=source_date).first()
    if source is None or not source.items:
        flash("There is no saved meal plan to copy from that date.", "error")
        return redirect(url_for("calendar.index", date=target_date.isoformat()))
    target = MealPlan.query.filter_by(user_id=current_user.id, plan_date=target_date).first()
    if target is None:
        target = MealPlan(user_id=current_user.id, plan_date=target_date, title="Copied meal plan")
        db.session.add(target)
        db.session.flush()
    target.items.clear()
    for item in source.items:
        target.items.append(MealItem(food_id=item.food_id, meal_type=item.meal_type, planned_time=item.planned_time, servings=item.servings, recommendation_reason=item.recommendation_reason))
    db.session.commit()
    flash(f"Meal plan copied to {target_date.strftime('%B %d')}.", "success")
    return redirect(url_for("calendar.index", date=target_date.isoformat()))
