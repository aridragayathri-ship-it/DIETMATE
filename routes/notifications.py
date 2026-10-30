"""In-app reminders and notification read state."""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from extensions import db
from models import Notification
from services.notifications import generate_reminders, local_now

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.get("/")
@login_required
def index():
    generate_reminders(current_user)
    items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc(), Notification.id.desc()).limit(100).all()
    return render_template("notifications/index.html", items=items, now=local_now())


@notifications_bp.post("/<int:notification_id>/read")
@login_required
def mark_read(notification_id):
    item = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    if item.read_at is None:
        item.read_at = local_now().replace(tzinfo=None)
        db.session.commit()
    return redirect(url_for("notifications.index"))


@notifications_bp.post("/read-all")
@login_required
def mark_all_read():
    now = local_now().replace(tzinfo=None)
    Notification.query.filter_by(user_id=current_user.id, read_at=None).update({"read_at": now})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications.index"))
