"""Database model package."""
from extensions import db
from models.user import User, UserProfile
from models.food import Food
from models.recipe import Recipe, RecipeIngredient, FavoriteRecipe
from models.meal import MealPlan, MealItem
from models.nutrition import DailyFoodLog
from models.water import WaterLog
from models.shopping import ShoppingList, ShoppingItem
from models.notification import Notification

__all__ = ["db", "User", "UserProfile", "Food", "Recipe", "RecipeIngredient", "FavoriteRecipe", "MealPlan", "MealItem", "DailyFoodLog", "WaterLog", "ShoppingList", "ShoppingItem", "Notification"]
