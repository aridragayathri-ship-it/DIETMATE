"""Profile and password management."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
DIETS = ["Vegetarian", "Vegan", "Pescatarian", "Non-vegetarian"]
ACTIVITY = ["Sedentary", "Light", "Moderate", "Active", "Very active"]
GOALS = ["Weight gain", "Weight loss", "Weight maintenance", "Healthy eating"]


def optional_number(field, cast, label, minimum, maximum):
    raw = request.form.get(field, "").strip()
    if not raw:
        return None
    try:
        value = cast(raw)
    except (ValueError, TypeError):
        raise ValueError(f"{label} must be a number.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return value


def nutrition_estimates(profile):
    bmi = None
    if profile.height_cm and profile.weight_kg:
        bmi = profile.weight_kg / ((profile.height_cm / 100) ** 2)
    calories = None
    if profile.age and profile.height_cm and profile.weight_kg:
        # Mifflin-St Jeor estimates use an optional gender input; unknown/unspecified uses midpoint.
        base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
        base += 5 if profile.gender == "Male" else (-161 if profile.gender == "Female" else -78)
        multiplier = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Very active": 1.9}.get(profile.activity_level, 1.55)
        calories = round(base * multiplier)
        if profile.fitness_goal == "Weight loss":
            calories = max(1200, calories - 300)
        elif profile.fitness_goal == "Weight gain":
            calories += 250
    return round(bmi, 1) if bmi else None, calories


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    if request.method == "POST":
        try:
            age = optional_number("age", int, "Age", 13, 120)
            height = optional_number("height_cm", float, "Height", 90, 250)
            weight = optional_number("weight_kg", float, "Weight", 25, 400)
            water_goal = optional_number("water_goal_ml", int, "Water goal", 250, 10000)
            name = request.form.get("full_name", "").strip()
            if not name or len(name) > 120:
                raise ValueError("Enter your name (up to 120 characters).")
            diet = request.form.get("dietary_preference", "")
            activity = request.form.get("activity_level", "")
            goal = request.form.get("fitness_goal", "")
            gender = request.form.get("gender", "")
            if diet not in DIETS or activity not in ACTIVITY or goal not in GOALS or gender not in ("", "Female", "Male", "Other"):
                raise ValueError("Choose a valid profile option.")
            current_user.full_name = name
            profile.age, profile.height_cm, profile.weight_kg = age, height, weight
            profile.gender = gender or None
            profile.dietary_preference, profile.activity_level, profile.fitness_goal = diet, activity, goal
            profile.allergies = request.form.get("allergies", "").strip()[:1000]
            profile.restrictions = request.form.get("restrictions", "").strip()[:1000]
            if water_goal:
                profile.water_goal_ml = water_goal
            db.session.commit()
            flash("Your profile has been updated.", "success")
            return redirect(url_for("profile.edit_profile"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
    bmi, calorie_target = nutrition_estimates(profile)
    return render_template("profile/edit.html", profile=profile, diets=DIETS, activities=ACTIVITY, goals=GOALS, bmi=bmi, calorie_target=calorie_target)


@profile_bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    from werkzeug.security import check_password_hash, generate_password_hash
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not check_password_hash(current_user.password_hash, current):
            flash("Your current password is incorrect.", "error")
        elif len(new) < 8:
            flash("Use a new password with at least 8 characters.", "error")
        elif new != confirm:
            flash("The new passwords do not match.", "error")
        else:
            current_user.password_hash = generate_password_hash(new)
            db.session.commit()
            flash("Your password has been changed.", "success")
            return redirect(url_for("profile.change_password"))
    return render_template("profile/password.html")
