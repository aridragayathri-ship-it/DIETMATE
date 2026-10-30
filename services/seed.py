"""Seed a small, editable starter food catalog for a fresh installation."""
from models import Food, Recipe, RecipeIngredient, db

STARTER_FOODS = [
    {"name": "Masala Oats", "category": "Breakfast", "calories": 285, "protein_g": 11, "carbs_g": 43, "fat_g": 7, "serving_size": "1 bowl", "preparation_minutes": 15, "dietary_classification": "Vegetarian", "description": "Warm oats with vegetables and gentle Indian spices.", "image_url": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?auto=format&fit=crop&w=720&q=85"},
    {"name": "Paneer Power Bowl", "category": "Lunch", "calories": 420, "protein_g": 24, "carbs_g": 48, "fat_g": 15, "serving_size": "1 bowl", "preparation_minutes": 25, "dietary_classification": "Vegetarian", "description": "Grilled paneer, grains and crisp seasonal vegetables.", "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=720&q=85"},
    {"name": "Berry Yogurt Parfait", "category": "Snack", "calories": 210, "protein_g": 12, "carbs_g": 29, "fat_g": 6, "serving_size": "1 glass", "preparation_minutes": 8, "dietary_classification": "Vegetarian", "description": "Creamy yogurt layered with berries, seeds and a little crunch.", "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=720&q=85"},
    {"name": "Vegetable Idli", "category": "Breakfast", "calories": 245, "protein_g": 9, "carbs_g": 46, "fat_g": 3, "serving_size": "3 idlis", "preparation_minutes": 20, "dietary_classification": "Vegetarian", "description": "Soft steamed idlis served with a bright vegetable sambar.", "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=720&q=85"},
    {"name": "Moong Sprout Chaat", "category": "Snack", "calories": 185, "protein_g": 13, "carbs_g": 27, "fat_g": 4, "serving_size": "1 bowl", "preparation_minutes": 12, "dietary_classification": "Vegan", "description": "Fresh sprouts tossed with cucumber, tomato and lime.", "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=720&q=85"},
    {"name": "Vegetable Poha", "category": "Breakfast", "calories": 290, "protein_g": 7, "carbs_g": 49, "fat_g": 7, "serving_size": "1 bowl", "preparation_minutes": 18, "dietary_classification": "Vegan", "description": "Lemon poha with peas, peanuts and fresh coriander.", "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=720&q=85"},
    {"name": "Masala Dosa", "category": "Breakfast", "calories": 340, "protein_g": 8, "carbs_g": 54, "fat_g": 10, "serving_size": "1 dosa", "preparation_minutes": 25, "dietary_classification": "Vegan", "description": "Crisp fermented rice crepe with spiced potato filling.", "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=720&q=85"},
    {"name": "Fruit and Seed Bowl", "category": "Fruit", "calories": 165, "protein_g": 4, "carbs_g": 30, "fat_g": 5, "serving_size": "1 bowl", "preparation_minutes": 7, "dietary_classification": "Vegan", "description": "Seasonal fruit with a sprinkle of seeds and lime.", "image_url": "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=720&q=85"},
    {"name": "Roasted Almonds", "category": "Snack", "calories": 175, "protein_g": 6, "carbs_g": 6, "fat_g": 15, "serving_size": "30 g", "preparation_minutes": 3, "dietary_classification": "Vegan", "description": "A measured handful of crunchy, heart-friendly nuts.", "image_url": "https://images.unsplash.com/photo-1508061253366-f7da158b6d46?auto=format&fit=crop&w=720&q=85"},
    {"name": "Dal and Rice", "category": "Lunch", "calories": 430, "protein_g": 18, "carbs_g": 67, "fat_g": 9, "serving_size": "1 plate", "preparation_minutes": 30, "dietary_classification": "Vegan", "description": "Comforting lentil dal served with steamed rice.", "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=720&q=85"},
    {"name": "Chapati Vegetable Curry", "category": "Lunch", "calories": 445, "protein_g": 14, "carbs_g": 66, "fat_g": 12, "serving_size": "2 chapatis + curry", "preparation_minutes": 30, "dietary_classification": "Vegan", "description": "Whole-wheat chapatis with a colorful seasonal curry.", "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=720&q=85"},
    {"name": "Vegetable Khichdi", "category": "Dinner", "calories": 390, "protein_g": 15, "carbs_g": 62, "fat_g": 8, "serving_size": "1 bowl", "preparation_minutes": 32, "dietary_classification": "Vegan", "description": "A gentle one-pot mix of rice, lentils and vegetables.", "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=720&q=85"},
    {"name": "Vegetable Pulao", "category": "Dinner", "calories": 420, "protein_g": 11, "carbs_g": 70, "fat_g": 11, "serving_size": "1 plate", "preparation_minutes": 30, "dietary_classification": "Vegan", "description": "Fragrant basmati rice cooked with vegetables and whole spices.", "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=720&q=85"},
    {"name": "Paneer Bhurji Roti", "category": "Dinner", "calories": 475, "protein_g": 26, "carbs_g": 45, "fat_g": 19, "serving_size": "1 plate", "preparation_minutes": 25, "dietary_classification": "Vegetarian", "description": "Spiced scrambled paneer with whole-wheat roti.", "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=720&q=85"},
]


def seed_foods():
    added = 0
    for row in STARTER_FOODS:
        if Food.query.filter_by(name=row["name"]).first() is None:
            db.session.add(Food(**row))
            added += 1
    if added:
        db.session.commit()
    return added


STARTER_RECIPES = {
    "Masala Oats": ("Heat oats with water or milk. Stir in sautéed vegetables and masala; simmer until creamy. Finish with lemon and herbs.", 12, [("Rolled oats", "½ cup"), ("Mixed vegetables", "½ cup"), ("Water or milk", "1 cup"), ("Masala", "½ tsp")]),
    "Paneer Power Bowl": ("Season and sear paneer until golden. Serve over cooked grains with fresh vegetables and a yogurt dressing.", 18, [("Paneer", "100 g"), ("Cooked grains", "¾ cup"), ("Seasonal vegetables", "1 cup"), ("Yogurt dressing", "2 tbsp")]),
    "Berry Yogurt Parfait": ("Layer yogurt, berries and seeds in a glass. Chill briefly and serve fresh.", 5, [("Greek yogurt", "¾ cup"), ("Mixed berries", "½ cup"), ("Chia seeds", "1 tsp"), ("Granola", "2 tbsp")]),
    "Vegetable Idli": ("Steam the fermented batter in idli moulds until fluffy. Serve warm with vegetable sambar.", 15, [("Idli batter", "1 cup"), ("Vegetable sambar", "¾ cup"), ("Curry leaves", "A few")]),
    "Moong Sprout Chaat": ("Toss sprouts with chopped cucumber and tomato. Season with lime, cumin and coriander; serve immediately.", 8, [("Moong sprouts", "1 cup"), ("Cucumber", "¼ cup"), ("Tomato", "¼ cup"), ("Lime juice", "1 tsp")]),
    "Vegetable Poha": ("Rinse flattened rice briefly. Temper mustard seeds, curry leaves and peanuts; sauté vegetables, fold in poha and finish with lemon.", 13, [("Flattened rice", "1 cup"), ("Peas", "¼ cup"), ("Peanuts", "1 tbsp"), ("Lemon", "½")]),
    "Masala Dosa": ("Spread fermented batter thinly on a hot pan. Add spiced potato filling, fold when crisp and serve with sambar.", 20, [("Dosa batter", "1 cup"), ("Potatoes", "1 medium"), ("Onion", "¼ cup"), ("Sambar", "½ cup")]),
    "Fruit and Seed Bowl": ("Chop seasonal fruit, add seeds and finish with fresh lime juice.", 5, [("Seasonal fruit", "1 cup"), ("Mixed seeds", "1 tsp"), ("Lime", "½")]),
    "Roasted Almonds": ("Toast almonds in a dry pan over low heat until fragrant. Cool before serving.", 3, [("Almonds", "30 g")]),
    "Dal and Rice": ("Simmer rinsed lentils with turmeric until soft. Temper with cumin and garlic, then serve with steamed rice.", 25, [("Red lentils", "½ cup"), ("Rice", "¾ cup cooked"), ("Turmeric", "¼ tsp"), ("Cumin", "½ tsp")]),
    "Chapati Vegetable Curry": ("Cook vegetables with tomato and spices until tender. Serve with warm whole-wheat chapatis.", 25, [("Whole-wheat flour", "2 chapatis"), ("Mixed vegetables", "1 cup"), ("Tomato", "1"), ("Spices", "To taste")]),
    "Vegetable Khichdi": ("Combine rice, lentils and vegetables with turmeric and water. Simmer covered until soft; temper with cumin.", 28, [("Rice", "⅓ cup"), ("Moong dal", "⅓ cup"), ("Mixed vegetables", "½ cup"), ("Turmeric", "¼ tsp")]),
    "Vegetable Pulao": ("Sauté whole spices and vegetables. Add rinsed basmati rice and measured water; cover and cook until fluffy.", 25, [("Basmati rice", "¾ cup"), ("Mixed vegetables", "1 cup"), ("Whole spices", "½ tsp"), ("Oil", "1 tsp")]),
    "Paneer Bhurji Roti": ("Sauté onion and tomato with spices, fold in crumbled paneer and cook briefly. Serve with warm roti.", 20, [("Paneer", "100 g"), ("Tomato", "½ cup"), ("Onion", "¼ cup"), ("Roti", "1")]),
}


def seed_recipes():
    added = 0
    for name, (instructions, cooking_minutes, ingredients) in STARTER_RECIPES.items():
        food = Food.query.filter_by(name=name, owner_id=None).first()
        if food and food.recipe is None:
            recipe = Recipe(food=food, instructions=instructions, cooking_minutes=cooking_minutes)
            recipe.ingredients = [RecipeIngredient(name=item, quantity=quantity) for item, quantity in ingredients]
            db.session.add(recipe)
            added += 1
    if added:
        db.session.commit()
    return added
