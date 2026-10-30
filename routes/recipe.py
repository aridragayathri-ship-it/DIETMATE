"""Recipe details and per-user favorites."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from extensions import db
from models import Food, FavoriteRecipe

recipe_bp = Blueprint("recipe", __name__, url_prefix="/recipes")


@recipe_bp.get("/<int:food_id>")
@login_required
def detail(food_id):
    food = Food.query.filter(Food.id == food_id, or_(Food.owner_id.is_(None), Food.owner_id == current_user.id)).first_or_404()
    return render_template("recipes/detail.html", food=food, recipe=food.recipe, is_favorite=bool(food.recipe and FavoriteRecipe.query.filter_by(user_id=current_user.id, recipe_id=food.recipe.id).first()))


@recipe_bp.post("/<int:food_id>/favorite")
@login_required
def toggle_favorite(food_id):
    food = Food.query.filter(Food.id == food_id, or_(Food.owner_id.is_(None), Food.owner_id == current_user.id)).first_or_404()
    if food.recipe is None:
        flash("This food does not have a recipe yet.", "error")
    else:
        favorite = FavoriteRecipe.query.filter_by(user_id=current_user.id, recipe_id=food.recipe.id).first()
        if favorite:
            db.session.delete(favorite)
            flash("Recipe removed from favorites.", "success")
        else:
            db.session.add(FavoriteRecipe(user_id=current_user.id, recipe_id=food.recipe.id))
            flash("Recipe saved to favorites.", "success")
        db.session.commit()
    return redirect(url_for("recipe.detail", food_id=food.id))
