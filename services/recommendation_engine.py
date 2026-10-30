"""Public recommendation service interface."""
from services.meal_engine import build_recommendations, calorie_target, recommendation_for_slot, suitable_foods

__all__ = ["build_recommendations", "calorie_target", "recommendation_for_slot", "suitable_foods"]
