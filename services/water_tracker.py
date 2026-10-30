"""Water intake summaries. Zero-amount rows are reset markers; intake history stays intact."""
from datetime import datetime, time, timedelta
from models import WaterLog


def day_logs(user_id, day):
    start = datetime.combine(day, time.min)
    end = datetime.combine(day + timedelta(days=1), time.min)
    return WaterLog.query.filter(WaterLog.user_id == user_id, WaterLog.logged_at >= start, WaterLog.logged_at < end).order_by(WaterLog.id.asc()).all()


def water_summary(user_id, day, goal_ml):
    logs = day_logs(user_id, day)
    # The log id captures when a drink was recorded, even when its display time was backdated.
    last_reset = next((row.id for row in reversed(logs) if row.amount_ml == 0), 0)
    active_logs = [row for row in logs if row.amount_ml > 0 and row.id > last_reset]
    amount = sum(row.amount_ml for row in active_logs)
    percent = min(100, round(amount / goal_ml * 100)) if goal_ml else 0
    cup_count = max(1, min(8, (goal_ml + 249) // 250))
    filled_cups = min(cup_count, round(percent * cup_count / 100))
    last_intake = active_logs[-1].logged_at.strftime("%I:%M %p").lstrip("0") if active_logs else None
    return {"amount_ml": amount, "goal_ml": goal_ml, "remaining_ml": max(0, goal_ml - amount), "percent": percent,
            "glasses": amount // 250, "last_intake": last_intake, "cup_count": cup_count, "filled_cups": filled_cups,
            "logs": list(reversed(logs))}


def weekly_totals(user_id, selected):
    values = []
    for offset in range(6, -1, -1):
        day = selected - timedelta(days=offset)
        values.append({"date": day, "amount_ml": sum(row.amount_ml for row in day_logs(user_id, day))})
    return values
