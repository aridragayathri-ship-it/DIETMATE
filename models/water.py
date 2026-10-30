from datetime import datetime
from extensions import db


class WaterLog(db.Model):
    __tablename__ = "water_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_ml = db.Column(db.Integer, nullable=False)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
