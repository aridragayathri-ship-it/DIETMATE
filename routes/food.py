"""Searchable catalog and owned food CRUD."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from extensions import db
from models import Food, Recipe, RecipeIngredient

food_bp = Blueprint("food", __name__, url_prefix="/foods")
CATEGORIES = ["Breakfast", "Lunch", "Snack", "Dinner", "Meal", "Fruit", "Other"]
DIETS = ["Vegetarian", "Vegan", "Pescatarian", "Non-vegetarian"]


def visible_food(food_id):
    food = Food.query.filter(Food.id == food_id, or_(Food.owner_id.is_(None), Food.owner_id == current_user.id)).first()
    if food is None:
        abort(404)
    return food


def catalog_query():
    return Food.query.filter(or_(Food.owner_id.is_(None), Food.owner_id == current_user.id))


def parse_ingredients(value):
    output = []
    for line in value.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            name, quantity = (part.strip() for part in line.split("|", 1))
        elif " - " in line:
            name, quantity = (part.strip() for part in line.split(" - ", 1))
        else:
            name, quantity = line, "As needed"
        if not name or len(name) > 120 or len(quantity) > 80:
            raise ValueError("Ingredient names must be under 120 characters and quantities under 80.")
        output.append(RecipeIngredient(name=name, quantity=quantity or "As needed"))
    if len(output) > 40:
        raise ValueError("A recipe can have at most 40 ingredients.")
    return output


def food_form_values():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "")
    diet = request.form.get("dietary_classification", "")
    serving = request.form.get("serving_size", "").strip()
    image = request.form.get("image_url", "").strip()
    instructions = request.form.get("instructions", "").strip()
    if not name or len(name) > 120 or len(description) > 280:
        raise ValueError("Enter a food name (up to 120 characters) and a description under 280 characters.")
    if category not in CATEGORIES or diet not in DIETS:
        raise ValueError("Choose a valid category and dietary classification.")
    if not serving or len(serving) > 60 or len(image) > 500:
        raise ValueError("Enter a serving size under 60 characters and an image URL under 500 characters.")
    def number(field, minimum, maximum):
        try:
            parsed = float(request.form.get(field, ""))
        except (TypeError, ValueError):
            raise ValueError(f"{field.replace('_', ' ').capitalize()} must be a number.")
        if not minimum <= parsed <= maximum:
            raise ValueError(f"{field.replace('_', ' ').capitalize()} must be between {minimum} and {maximum}.")
        return parsed
    calories = number("calories", 0, 5000)
    protein = number("protein_g", 0, 500)
    carbs = number("carbs_g", 0, 1000)
    fat = number("fat_g", 0, 500)
    prep = int(number("preparation_minutes", 0, 1440))
    cooking = int(number("cooking_minutes", 0, 1440))
    if len(instructions) > 10000:
        raise ValueError("Recipe instructions must be under 10,000 characters.")
    ingredients = parse_ingredients(request.form.get("ingredients", ""))
    return locals()


@food_bp.get("/")
@login_required
def index():
    query = request.args.get("q", "").strip()[:100]
    category = request.args.get("category", "")
    diet = request.args.get("diet", "")
    foods = catalog_query()
    if query:
        pattern = f"%{query}%"
        foods = foods.filter(or_(Food.name.ilike(pattern), Food.description.ilike(pattern), Food.category.ilike(pattern)))
    if category in CATEGORIES:
        foods = foods.filter_by(category=category)
    if diet in DIETS:
        foods = foods.filter_by(dietary_classification=diet)
    return render_template("food/index.html", foods=foods.order_by(Food.category, Food.name).all(), query=query, category=category, diet=diet, categories=CATEGORIES, diets=DIETS)


@food_bp.get("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()[:80]
    if len(query) < 2:
        return jsonify(results=[])
    foods = catalog_query().filter(or_(Food.name.ilike(f"%{query}%"), Food.category.ilike(f"%{query}%"))).order_by(Food.name).limit(8).all()
    return jsonify(results=[{"id": food.id, "name": food.name, "category": food.category, "url": url_for("recipe.detail", food_id=food.id)} for food in foods])


@food_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        try:
            values = food_form_values()
            food = Food(owner_id=current_user.id, name=values["name"], description=values["description"], category=values["category"], dietary_classification=values["diet"], serving_size=values["serving"], image_url=values["image"], calories=values["calories"], protein_g=values["protein"], carbs_g=values["carbs"], fat_g=values["fat"], preparation_minutes=values["prep"])
            food.recipe = Recipe(instructions=values["instructions"], cooking_minutes=values["cooking"], ingredients=values["ingredients"])
            db.session.add(food)
            db.session.commit()
            flash("Food and recipe added to your database.", "success")
            return redirect(url_for("recipe.detail", food_id=food.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
    return render_template("food/form.html", food=None, categories=CATEGORIES, diets=DIETS, recipe=None, ingredient_text="")


@food_bp.route("/<int:food_id>/edit", methods=["GET", "POST"])
@login_required
def edit(food_id):
    food = visible_food(food_id)
    if food.owner_id != current_user.id:
        abort(403)
    recipe = food.recipe
    if request.method == "POST":
        try:
            values = food_form_values()
            for key, attr in [("name", "name"), ("description", "description"), ("category", "category"), ("diet", "dietary_classification"), ("serving", "serving_size"), ("image", "image_url"), ("calories", "calories"), ("protein", "protein_g"), ("carbs", "carbs_g"), ("fat", "fat_g"), ("prep", "preparation_minutes")]:
                setattr(food, attr, values[key])
            if recipe is None:
                recipe = Recipe(food=food)
            recipe.instructions, recipe.cooking_minutes = values["instructions"], values["cooking"]
            recipe.ingredients[:] = values["ingredients"]
            db.session.commit()
            flash("Food and recipe updated.", "success")
            return redirect(url_for("recipe.detail", food_id=food.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
    ingredient_text = "\n".join(f"{item.name} | {item.quantity}" for item in recipe.ingredients) if recipe else ""
    return render_template("food/form.html", food=food, categories=CATEGORIES, diets=DIETS, recipe=recipe, ingredient_text=ingredient_text)


@food_bp.post("/<int:food_id>/delete")
@login_required
def delete(food_id):
    food = visible_food(food_id)
    if food.owner_id != current_user.id:
        abort(403)
    db.session.delete(food)
    db.session.commit()
    flash("Food removed from your database.", "success")
    return redirect(url_for("food.index"))
