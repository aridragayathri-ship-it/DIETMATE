from datetime import date
from extensions import db


class MealPlan(db.Model):
    __tablename__ = "meal_plans"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    title = db.Column(db.String(120), nullable=False, default="Daily meal plan")
    user = db.relationship("User", back_populates="meal_plans")
    items = db.relationship("MealItem", back_populates="plan", cascade="all, delete-orphan")


class MealItem(db.Model):
    __tablename__ = "meal_items"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id", ondelete="SET NULL"))
    meal_type = db.Column(db.String(40), nullable=False)
    planned_time = db.Column(db.String(10), nullable=False, default="08:00")
    servings = db.Column(db.Float, nullable=False, default=1)
    recommendation_reason = db.Column(db.String(500), nullable=False, default="")
    plan = db.relationship("MealPlan", back_populates="items")
    food = db.relationship("Food")
