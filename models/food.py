from extensions import db


class Food(db.Model):
    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False, default="Meal")
    calories = db.Column(db.Float, nullable=False, default=0)
    protein_g = db.Column(db.Float, nullable=False, default=0)
    carbs_g = db.Column(db.Float, nullable=False, default=0)
    fat_g = db.Column(db.Float, nullable=False, default=0)
    serving_size = db.Column(db.String(60), nullable=False, default="1 serving")
    dietary_classification = db.Column(db.String(80), nullable=False, default="Vegetarian")
    preparation_minutes = db.Column(db.Integer, nullable=False, default=15)
    image_url = db.Column(db.String(500), default="")
    description = db.Column(db.String(280), default="")
    recipe = db.relationship("Recipe", back_populates="food", uselist=False, cascade="all, delete-orphan")
