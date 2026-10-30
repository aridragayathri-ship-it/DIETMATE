"""Create deduplicated in-app reminders when the user opens notifications."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from flask import current_app
from models import DailyFoodLog, MealPlan, Notification
from services.water_tracker import water_summary


def local_now():
    try:
        zone = ZoneInfo(current_app.config.get("DIETMATE_TIMEZONE", "Asia/Kolkata"))
    except Exception:
        zone = ZoneInfo("UTC")
    return datetime.now(zone)


def generate_reminders(user, now=None):
    now = now or local_now()
    today = now.date()
    profile = user.profile
    if not profile:
        return 0
    candidates = []
    if profile.meal_reminders:
        plan = MealPlan.query.filter_by(user_id=user.id, plan_date=today).first()
        if plan:
            for item in plan.items:
                try:
                    meal_time = datetime.strptime(item.planned_time, "%H:%M").time()
                    meal_dt = now.replace(hour=meal_time.hour, minute=meal_time.minute, second=0, microsecond=0)
                    delta = (meal_dt - now).total_seconds() / 60
                except ValueError:
                    continue
                if 0 <= delta <= 30:
                    candidates.append(("meal", f"meal:{today}:{item.id}", f"{item.meal_type} is coming up", f"{item.food.name if item.food else 'Your meal'} is planned for {item.planned_time}."))
    if profile.water_reminders and now.hour >= 8:
        hydration = water_summary(user.id, today, profile.water_goal_ml)
        recent = hydration["logs"]
        last_record = next((row for row in recent if row.amount_ml > 0 and row.id > next((mark.id for mark in recent if mark.amount_ml == 0), 0)), None)
        should_remind = hydration["amount_ml"] < profile.water_goal_ml and (not last_record or (now.replace(tzinfo=None) - last_record.logged_at) >= timedelta(hours=2))
        if should_remind:
            candidates.append(("water", f"water:{today}:{now.hour // 2}", "Time for a water break", f"You have {hydration['remaining_ml']:,} ml left toward today's water goal."))
    if profile.tracking_reminders and now.hour >= 19:
        logged = DailyFoodLog.query.filter(DailyFoodLog.user_id == user.id, DailyFoodLog.logged_at >= datetime.combine(today, datetime.min.time()), DailyFoodLog.logged_at < datetime.combine(today + timedelta(days=1), datetime.min.time())).count()
        if logged == 0:
            candidates.append(("tracking", f"tracking:{today}", "Complete today's food log", "You have not logged any food today. Add meals to keep your nutrition history up to date."))
    added = 0
    for category, key, title, body in candidates:
        exists = Notification.query.filter_by(user_id=user.id, dedupe_key=key).first()
        if not exists:
            from extensions import db
            db.session.add(Notification(user_id=user.id, category=category, dedupe_key=key, title=title, body=body))
            added += 1
    if added:
        from extensions import db
        db.session.commit()
    return added
