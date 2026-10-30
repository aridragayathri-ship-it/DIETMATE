"""Aggregate logged servings into daily nutrition totals and targets."""
from datetime import datetime, time, timedelta
from models import DailyFoodLog
from services.meal_engine import calorie_target


def day_bounds(day):
    return datetime.combine(day, time.min), datetime.combine(day + timedelta(days=1), time.min)


def logs_for_day(user_id, day):
    start, end = day_bounds(day)
    return (DailyFoodLog.query.filter(DailyFoodLog.user_id == user_id, DailyFoodLog.logged_at >= start, DailyFoodLog.logged_at < end)
            .order_by(DailyFoodLog.logged_at.desc()).all())


def totals_for_logs(logs):
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for log in logs:
        if log.food is None:
            continue
        for key in totals:
            totals[key] += getattr(log.food, key) * log.servings
    return {key: round(value, 1) for key, value in totals.items()}


def daily_summary(user, day):
    logs = logs_for_day(user.id, day)
    totals = totals_for_logs(logs)
    target, personalized = calorie_target(user.profile)
    protein_target = round(target * 0.20 / 4)
    carbs_target = round(target * 0.50 / 4)
    fat_target = round(target * 0.30 / 9)
    return {
        "logs": logs,
        "totals": totals,
        "targets": {"calories": target, "protein_g": protein_target, "carbs_g": carbs_target, "fat_g": fat_target},
        "personalized": personalized,
    }
