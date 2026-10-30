"""User reminder preferences and application settings."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    profile = current_user.profile
    if request.method == "POST":
        profile.meal_reminders = request.form.get("meal_reminders") == "on"
        profile.water_reminders = request.form.get("water_reminders") == "on"
        profile.tracking_reminders = request.form.get("tracking_reminders") == "on"
        db.session.commit()
        flash("Reminder preferences saved.", "success")
        return redirect(url_for("settings.index"))
    return render_template("settings/index.html", profile=profile)
