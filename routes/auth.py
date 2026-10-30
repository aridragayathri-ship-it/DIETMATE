"""Registration and session routes."""
from urllib.parse import urljoin, urlparse
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import User, UserProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def safe_next(target):
    if not target:
        return None
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return target if test.scheme in ("http", "https") and ref.netloc == test.netloc else None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name or len(name) > 120:
            flash("Enter your name (up to 120 characters).", "error")
        elif "@" not in email or len(email) > 254:
            flash("Enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif password != confirm:
            flash("The passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Please sign in.", "error")
        else:
            user = User(full_name=name, email=email, password_hash=generate_password_hash(password))
            user.profile = UserProfile()
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account is ready. Welcome to DietMate!", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=request.form.get("remember") == "on")
            flash("Welcome back!", "success")
            return redirect(safe_next(request.args.get("next")) or url_for("dashboard.index"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth/login.html")


@auth_bp.get("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
