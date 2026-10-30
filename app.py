"""DietMate Flask application entry point."""
from pathlib import Path
from flask import Flask, jsonify
from flask_login import current_user
from config import Config
from extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)

    from models import User, UserProfile, Food, Recipe, RecipeIngredient, FavoriteRecipe, MealPlan, MealItem, DailyFoodLog, WaterLog, ShoppingList, ShoppingItem, Notification  # noqa: F401
    from routes.dashboard import dashboard_bp
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.food import food_bp
    from routes.recipe import recipe_bp
    from routes.meal import meal_bp
    from routes.nutrition import nutrition_bp
    from routes.water import water_bp
    from routes.shopping import shopping_bp
    from routes.calendar import calendar_bp
    from routes.reports import reports_bp
    from routes.notifications import notifications_bp
    from routes.settings import settings_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(meal_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(settings_bp)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @app.context_processor
    def notification_badge():
        count = 0
        if current_user.is_authenticated:
            from models import Notification
            count = Notification.query.filter_by(user_id=current_user.id, read_at=None).count()
        return {"unread_notifications": count}

    @app.get("/health")
    def health():
        return jsonify(status="ok", app="DietMate")

    with app.app_context():
        db.create_all()
        # Upgrade installations created during Phase 1 before applying this feature.
        from sqlalchemy import inspect, text
        if "owner_id" not in {column["name"] for column in inspect(db.engine).get_columns("foods")}:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE foods ADD COLUMN owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
        with db.engine.begin() as connection:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_foods_owner_id ON foods(owner_id)"))
        if "recommendation_reason" not in {column["name"] for column in inspect(db.engine).get_columns("meal_items")}:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE meal_items ADD COLUMN recommendation_reason VARCHAR(500) NOT NULL DEFAULT ''"))
        # Lightweight upgrades for project-local SQLite files created in earlier phases.
        upgrades = {
            "user_profiles": {"meal_reminders": "BOOLEAN NOT NULL DEFAULT 1", "water_reminders": "BOOLEAN NOT NULL DEFAULT 1", "tracking_reminders": "BOOLEAN NOT NULL DEFAULT 1"},
            "shopping_lists": {"start_date": "DATE", "end_date": "DATE", "created_at": "DATETIME"},
            "shopping_items": {"category": "VARCHAR(40) NOT NULL DEFAULT 'Other'"},
        }
        for table, columns in upgrades.items():
            existing = {column["name"] for column in inspect(db.engine).get_columns(table)}
            for column, sql_type in columns.items():
                if column not in existing:
                    with db.engine.begin() as connection:
                        connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
        from services.seed import seed_foods, seed_recipes
        seed_foods()
        seed_recipes()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
