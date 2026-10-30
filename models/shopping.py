from datetime import datetime
from extensions import db


class ShoppingList(db.Model):
    __tablename__ = "shopping_lists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False, default="Weekly essentials")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingItem(db.Model):
    __tablename__ = "shopping_items"
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.String(60), nullable=False, default="1")
    purchased = db.Column(db.Boolean, nullable=False, default=False)
    category = db.Column(db.String(40), nullable=False, default="Other")
    shopping_list = db.relationship("ShoppingList", back_populates="items")
