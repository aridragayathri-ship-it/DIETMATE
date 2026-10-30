from extensions import db


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    instructions = db.Column(db.Text, nullable=False, default="")
    cooking_minutes = db.Column(db.Integer, nullable=False, default=15)
    food = db.relationship("Food", back_populates="recipe")
    ingredients = db.relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeIngredient.id")


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.String(80), nullable=False, default="As needed")
    recipe = db.relationship("Recipe", back_populates="ingredients")


class FavoriteRecipe(db.Model):
    __tablename__ = "favorite_recipes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint("user_id", "recipe_id", name="uq_user_favorite_recipe"),)
