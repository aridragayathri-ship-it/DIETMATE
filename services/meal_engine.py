"""Transparent, constraint-aware meal recommendations (estimates, not prescriptions)."""
from datetime import timedelta
from sqlalchemy import or_
from models import Food, MealPlan

MEAL_SLOTS = [
    {"name": "Breakfast", "time": "08:00", "share": 0.25, "categories": ["Breakfast"]},
    {"name": "Morning Snack", "time": "10:30", "share": 0.10, "categories": ["Snack", "Fruit"]},
    {"name": "Lunch", "time": "13:00", "share": 0.30, "categories": ["Lunch"]},
    {"name": "Evening Snack", "time": "16:30", "share": 0.10, "categories": ["Snack", "Fruit"]},
    {"name": "Dinner", "time": "19:30", "share": 0.25, "categories": ["Dinner"]},
]
DIET_ALIASES = {"Vegetarian": {"Vegetarian", "Vegan"}, "Vegan": {"Vegan"}, "Pescatarian": {"Vegetarian", "Vegan", "Pescatarian"}, "Non-vegetarian": {"Vegetarian", "Vegan", "Pescatarian", "Non-vegetarian"}}


def calorie_target(profile):
    """Estimate a daily energy target from profile data; use a neutral fallback if incomplete."""
    if not profile or not all((profile.age, profile.height_cm, profile.weight_kg)):
        return 1800, False
    base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
    base += 5 if profile.gender == "Male" else (-161 if profile.gender == "Female" else -78)
    activity = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Very active": 1.9}.get(profile.activity_level, 1.55)
    target = round(base * activity)
    if profile.fitness_goal == "Weight loss":
        target = max(1200, target - 300)
    elif profile.fitness_goal == "Weight gain":
        target += 250
    return max(1000, min(target, 4500)), True


def _tokens(value):
    return [part.strip().lower() for part in (value or "").replace(";", ",").replace("\n", ",").split(",") if part.strip()]


def suitable_foods(user):
    profile = user.profile
    foods = Food.query.filter(or_(Food.owner_id.is_(None), Food.owner_id == user.id)).order_by(Food.id).all()
    allowed = DIET_ALIASES.get(profile.dietary_preference if profile else "Vegetarian", DIET_ALIASES["Vegetarian"])
    avoid = _tokens((profile.allergies if profile else "") + "," + (profile.restrictions if profile else ""))
    filtered = []
    for food in foods:
        if food.dietary_classification not in allowed:
            continue
        searchable = " ".join([food.name, food.description or "", food.category, *(item.name for item in food.recipe.ingredients)]).lower() if food.recipe else f"{food.name} {food.description or ''} {food.category}".lower()
        if any(term in searchable for term in avoid):
            continue
        filtered.append(food)
    return filtered


def _recent_food_ids(user, plan_date):
    after = plan_date - timedelta(days=6)
    plans = MealPlan.query.filter(MealPlan.user_id == user.id, MealPlan.plan_date >= after, MealPlan.plan_date < plan_date).all()
    return {item.food_id for plan in plans for item in plan.items if item.food_id}


def recommendation_for_slot(user, slot, chosen_ids=(), plan_date=None):
    target, measured = calorie_target(user.profile)
    slot_target = target * slot["share"]
    suitable = suitable_foods(user)
    candidates = [food for food in suitable if food.category in slot["categories"]]
    if not candidates:
        candidates = [food for food in suitable if food.category in ("Meal", "Other")]
    if not candidates:
        candidates = suitable
    if not candidates:
        return None, "No foods match your dietary preference and restrictions. Add a suitable food to the database first."
    recent = _recent_food_ids(user, plan_date) if plan_date else set()
    chosen_ids = set(chosen_ids)
    def score(food):
        value = abs(food.calories - slot_target) / max(slot_target, 100)
        if food.id in recent:
            value += 0.35
        if food.id in chosen_ids:
            value += 2.0
        return value
    selected = min(candidates, key=lambda food: (score(food), food.id))
    diet = user.profile.dietary_preference if user.profile else "Vegetarian"
    proximity = round(abs(selected.calories - slot_target))
    target_note = f"about {int(round(slot_target))} kcal for this meal" if measured else f"about {int(round(slot_target))} kcal using the 1,800 kcal starter target"
    reason = f"{selected.dietary_classification} choice matches your {diet.lower()} preference; {selected.calories:g} kcal is {proximity} kcal from {target_note}."
    if selected.id in recent:
        reason += " It is repeated because few suitable foods matched this meal slot."
    return selected, reason


def build_recommendations(user, plan_date):
    result, selected_ids = [], set()
    for slot in MEAL_SLOTS:
        food, reason = recommendation_for_slot(user, slot, selected_ids, plan_date)
        if food:
            result.append({"slot": slot, "food": food, "reason": reason})
            selected_ids.add(food.id)
    return result
