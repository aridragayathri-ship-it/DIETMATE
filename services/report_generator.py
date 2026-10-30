"""Generate user-scoped daily, weekly, and monthly analytics datasets."""
import calendar
from datetime import date, datetime, timedelta
from models import DailyFoodLog, MealPlan, ShoppingList, WaterLog
from services.nutrition_calculator import day_bounds, totals_for_logs


def report_range(period, selected):
    if period == "daily":
        return selected, selected
    if period == "monthly":
        start = selected.replace(day=1)
        end = selected.replace(day=calendar.monthrange(selected.year, selected.month)[1])
        return start, end
    return selected - timedelta(days=6), selected


def build_report(user, period, selected):
    start, end = report_range(period, selected)
    days = []
    cursor = start
    while cursor <= end:
        lower, upper = day_bounds(cursor)
        logs = DailyFoodLog.query.filter(DailyFoodLog.user_id == user.id, DailyFoodLog.logged_at >= lower, DailyFoodLog.logged_at < upper).all()
        water = WaterLog.query.filter(WaterLog.user_id == user.id, WaterLog.logged_at >= lower, WaterLog.logged_at < upper, WaterLog.amount_ml > 0).all()
        plans = MealPlan.query.filter_by(user_id=user.id, plan_date=cursor).all()
        totals = totals_for_logs(logs)
        days.append({"date": cursor, **totals, "water_ml": sum(row.amount_ml for row in water), "food_entries": len(logs), "planned_meals": sum(len(plan.items) for plan in plans)})
        cursor += timedelta(days=1)
    shopping_lists = ShoppingList.query.filter(ShoppingList.user_id == user.id, ShoppingList.created_at >= datetime.combine(start, datetime.min.time()), ShoppingList.created_at < datetime.combine(end + timedelta(days=1), datetime.min.time())).all()
    shopping_total = sum(len(row.items) for row in shopping_lists)
    shopping_purchased = sum(sum(item.purchased for item in row.items) for row in shopping_lists)
    return {"start": start, "end": end, "days": days,
            "totals": {key: round(sum(row[key] for row in days), 1) for key in ("calories", "protein_g", "carbs_g", "fat_g", "water_ml", "food_entries", "planned_meals")},
            "shopping_lists": shopping_lists, "shopping_total": shopping_total, "shopping_purchased": shopping_purchased}
