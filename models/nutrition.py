from datetime import datetime
from extensions import db


class DailyFoodLog(db.Model):
    __tablename__ = "daily_food_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id", ondelete="SET NULL"))
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    servings = db.Column(db.Float, nullable=False, default=1)
    food = db.relationship("Food")
