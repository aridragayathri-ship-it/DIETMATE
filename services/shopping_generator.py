"""Build categorized shopping items from recipe ingredients in meal plans."""
import re

FRACTIONS = {"½": 0.5, "⅓": 1/3, "⅔": 2/3, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875}


def _quantity_parts(value):
    text = (value or "As needed").strip().lower()
    for glyph, decimal in FRACTIONS.items():
        text = text.replace(glyph, f" {decimal} ")
    match = re.match(r"^\s*(\d+\s*/\s*\d+|\d+(?:\.\d+)?)?\s*(.*?)\s*$", text)
    if not match or not match.group(1):
        return None, text
    number_text = match.group(1).replace(" ", "")
    try:
        amount = float(number_text.split("/")[0]) / float(number_text.split("/")[1]) if "/" in number_text else float(number_text)
    except (ValueError, ZeroDivisionError):
        return None, text
    return amount, match.group(2).strip()


def categorize_ingredient(name):
    name = name.lower()
    categories = {
        "Produce": ("vegetable", "tomato", "onion", "cucumber", "lemon", "lime", "fruit", "berry", "berries", "spinach", "peas", "potato", "coriander", "curry leaves"),
        "Dairy & chilled": ("paneer", "milk", "yogurt", "curd", "cheese", "butter"),
        "Protein & pulses": ("dal", "lentil", "sprout", "chickpea", "bean", "tofu", "egg", "chicken", "fish"),
        "Grains & bakery": ("rice", "oat", "flour", "roti", "chapati", "bread", "semolina", "poha", "batter", "granola"),
        "Nuts & seeds": ("nut", "almond", "peanut", "seed", "chia"),
        "Spices & pantry": ("spice", "masala", "cumin", "turmeric", "oil", "salt", "water", "whole spices"),
    }
    for category, terms in categories.items():
        if any(term in name for term in terms):
            return category
    return "Other"


def combine_recipe_ingredients(meal_items):
    combined = {}
    for meal in meal_items:
        if not meal.food or not meal.food.recipe:
            continue
        servings = meal.servings or 1
        for ingredient in meal.food.recipe.ingredients:
            key = ingredient.name.strip().casefold()
            if not key:
                continue
            amount, unit = _quantity_parts(ingredient.quantity)
            record = combined.setdefault(key, {"name": ingredient.name.strip(), "category": categorize_ingredient(ingredient.name), "amounts": {}, "notes": []})
            if amount is None:
                record["notes"].append(ingredient.quantity.strip())
            else:
                record["amounts"][unit] = record["amounts"].get(unit, 0) + amount * servings
    result = []
    for entry in combined.values():
        parts = [f"{amount:g} {unit}".strip() for unit, amount in sorted(entry["amounts"].items())]
        parts.extend(sorted(set(entry["notes"])))
        result.append({"name": entry["name"], "category": entry["category"], "quantity": " + ".join(parts) if parts else "As needed"})
    return sorted(result, key=lambda row: (row["category"], row["name"].casefold()))
