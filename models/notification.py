from datetime import datetime
from extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    dedupe_key = db.Column(db.String(180), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    user = db.relationship("User")
    __table_args__ = (db.UniqueConstraint("user_id", "dedupe_key", name="uq_user_notification_key"),)
