from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False, default="DietMate member")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profile = db.relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    meal_plans = db.relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")


class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = db.Column(db.Integer)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    gender = db.Column(db.String(30))
    dietary_preference = db.Column(db.String(40), nullable=False, default="Vegetarian")
    activity_level = db.Column(db.String(40), nullable=False, default="Moderate")
    fitness_goal = db.Column(db.String(50), nullable=False, default="Healthy eating")
    allergies = db.Column(db.Text, default="")
    restrictions = db.Column(db.Text, default="")
    water_goal_ml = db.Column(db.Integer, nullable=False, default=2000)
    meal_reminders = db.Column(db.Boolean, nullable=False, default=True)
    water_reminders = db.Column(db.Boolean, nullable=False, default=True)
    tracking_reminders = db.Column(db.Boolean, nullable=False, default=True)
    user = db.relationship("User", back_populates="profile")
