"""Shopping list management and meal-plan ingredient generation."""
import csv
from datetime import date, datetime, timedelta
from io import StringIO
from flask import Blueprint, abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from models import MealPlan, ShoppingItem, ShoppingList
from services.shopping_generator import combine_recipe_ingredients, categorize_ingredient

shopping_bp = Blueprint("shopping", __name__, url_prefix="/shopping")


def read_date(value, fallback):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return fallback


def owned_list(list_id):
    return ShoppingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()


def owned_item(list_id, item_id):
    return ShoppingItem.query.join(ShoppingList).filter(ShoppingItem.id == item_id, ShoppingItem.list_id == list_id, ShoppingList.user_id == current_user.id).first_or_404()


@shopping_bp.get("/")
@login_required
def index():
    lists = ShoppingList.query.filter_by(user_id=current_user.id).order_by(ShoppingList.created_at.desc(), ShoppingList.id.desc()).all()
    selected_id = request.args.get("list", type=int)
    selected = next((row for row in lists if row.id == selected_id), None) if selected_id else (lists[0] if lists else None)
    status = request.args.get("status", "all")
    items = list(selected.items) if selected else []
    if status == "pending":
        items = [item for item in items if not item.purchased]
    elif status == "purchased":
        items = [item for item in items if item.purchased]
    items.sort(key=lambda item: (item.category, item.name.casefold()))
    total = len(selected.items) if selected else 0
    purchased = sum(item.purchased for item in selected.items) if selected else 0
    return render_template("shopping/index.html", lists=lists, selected=selected, items=items, status=status, total=total, purchased=purchased,
                           today=date.today(), next_week=date.today() + timedelta(days=6))


@shopping_bp.post("/new")
@login_required
def create_list():
    title = request.form.get("title", "").strip() or "My shopping list"
    if len(title) > 120:
        flash("List titles must be 120 characters or fewer.", "error")
        return redirect(url_for("shopping.index"))
    shopping_list = ShoppingList(user_id=current_user.id, title=title)
    db.session.add(shopping_list)
    db.session.commit()
    flash("Shopping list created.", "success")
    return redirect(url_for("shopping.index", list=shopping_list.id))


@shopping_bp.post("/generate")
@login_required
def generate():
    start = read_date(request.form.get("start_date"), date.today())
    end = read_date(request.form.get("end_date"), start + timedelta(days=6))
    if end < start or (end - start).days > 30:
        flash("Choose a date range of 1 to 31 days.", "error")
        return redirect(url_for("shopping.index"))
    plans = MealPlan.query.filter(MealPlan.user_id == current_user.id, MealPlan.plan_date >= start, MealPlan.plan_date <= end).all()
    ingredients = combine_recipe_ingredients([item for plan in plans for item in plan.items])
    if not ingredients:
        flash("No recipe ingredients were found in meal plans for that date range.", "error")
        return redirect(url_for("shopping.index"))
    shopping_list = ShoppingList(user_id=current_user.id, title=f"Meal plan · {start.strftime('%b %d')}–{end.strftime('%b %d')}", start_date=start, end_date=end)
    shopping_list.items = [ShoppingItem(**row) for row in ingredients]
    db.session.add(shopping_list)
    db.session.commit()
    flash(f"Generated {len(ingredients)} combined ingredients from {len(plans)} meal plan(s).", "success")
    return redirect(url_for("shopping.index", list=shopping_list.id))


@shopping_bp.post("/<int:list_id>/add")
@login_required
def add_item(list_id):
    shopping_list = owned_list(list_id)
    name = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "1").strip()
    if not name or len(name) > 120 or not quantity or len(quantity) > 60:
        flash("Enter an item name up to 120 characters and a quantity up to 60 characters.", "error")
    else:
        normalized = name.casefold()
        existing = next((item for item in shopping_list.items if item.name.casefold() == normalized and not item.purchased), None)
        if existing:
            existing.quantity = f"{existing.quantity} + {quantity}"
        else:
            shopping_list.items.append(ShoppingItem(name=name, quantity=quantity, category=categorize_ingredient(name)))
        db.session.commit()
        flash(f"{name} added to the list.", "success")
    return redirect(url_for("shopping.index", list=list_id))


@shopping_bp.post("/<int:list_id>/edit/<int:item_id>")
@login_required
def edit_item(list_id, item_id):
    item = owned_item(list_id, item_id)
    name = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "").strip()
    if not name or len(name) > 120 or not quantity or len(quantity) > 60:
        flash("Enter a valid item name and quantity.", "error")
    else:
        item.name, item.quantity, item.category = name, quantity, categorize_ingredient(name)
        db.session.commit()
        flash("Shopping item updated.", "success")
    return redirect(url_for("shopping.index", list=list_id))


@shopping_bp.post("/<int:list_id>/toggle/<int:item_id>")
@login_required
def toggle_item(list_id, item_id):
    item = owned_item(list_id, item_id)
    item.purchased = not item.purchased
    db.session.commit()
    flash(f"{item.name} marked {'purchased' if item.purchased else 'pending'}.", "success")
    return redirect(url_for("shopping.index", list=list_id, status=request.form.get("status", "all")))


@shopping_bp.post("/<int:list_id>/delete/<int:item_id>")
@login_required
def delete_item(list_id, item_id):
    item = owned_item(list_id, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from your shopping list.", "success")
    return redirect(url_for("shopping.index", list=list_id))


@shopping_bp.post("/<int:list_id>/delete")
@login_required
def delete_list(list_id):
    shopping_list = owned_list(list_id)
    db.session.delete(shopping_list)
    db.session.commit()
    flash("Shopping list deleted.", "success")
    return redirect(url_for("shopping.index"))


@shopping_bp.get("/<int:list_id>/export.csv")
@login_required
def export_csv(list_id):
    shopping_list = owned_list(list_id)
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Item", "Quantity", "Category", "Purchased"])
    for item in sorted(shopping_list.items, key=lambda row: (row.category, row.name.casefold())):
        writer.writerow([item.name, item.quantity, item.category, "Yes" if item.purchased else "No"])
    response = make_response(stream.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=dietmate-shopping-{shopping_list.id}.csv"
    return response
