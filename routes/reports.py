"""Analytics screens and downloadable report CSVs."""
import csv
from datetime import date, datetime
from io import StringIO
from flask import Blueprint, make_response, render_template, request, url_for
from flask_login import current_user, login_required
from services.report_generator import build_report

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
PERIODS = {"daily", "weekly", "monthly"}


def selected_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


@reports_bp.get("/")
@login_required
def index():
    period = request.args.get("period", "weekly")
    if period not in PERIODS:
        period = "weekly"
    selected = selected_date(request.args.get("date"))
    report = build_report(current_user, period, selected)
    return render_template("reports/index.html", period=period, selected=selected, report=report,
                           labels=[row["date"].strftime("%b %d") for row in report["days"]],
                           calories=[row["calories"] for row in report["days"]],
                           macros=[report["totals"]["protein_g"], report["totals"]["carbs_g"], report["totals"]["fat_g"]],
                           csv_url=url_for("reports.export_csv", period=period, date=selected.isoformat()))


@reports_bp.get("/export.csv")
@login_required
def export_csv():
    period = request.args.get("period", "weekly")
    if period not in PERIODS:
        period = "weekly"
    selected = selected_date(request.args.get("date"))
    report = build_report(current_user, period, selected)
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Date", "Calories (kcal)", "Protein (g)", "Carbohydrates (g)", "Fat (g)", "Water (ml)", "Food log entries", "Planned meals"])
    for row in report["days"]:
        writer.writerow([row["date"].isoformat(), row["calories"], row["protein_g"], row["carbs_g"], row["fat_g"], row["water_ml"], row["food_entries"], row["planned_meals"]])
    writer.writerow(["TOTAL", *[report["totals"][key] for key in ("calories", "protein_g", "carbs_g", "fat_g", "water_ml", "food_entries", "planned_meals")]])
    writer.writerow([])
    writer.writerow(["Shopping lists created", len(report["shopping_lists"]), "Items", report["shopping_total"], "Purchased", report["shopping_purchased"]])
    response = make_response(stream.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=dietmate-{period}-report-{selected.isoformat()}.csv"
    return response
