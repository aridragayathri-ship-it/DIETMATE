# DietMate – Adaptive Meal Planner

DietMate is a Flask and SQLite meal-planning application. The current foundation provides the application factory, relational data model, starter food catalog, dashboard, account authentication, and profile management.

## Run on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

Open <http://127.0.0.1:5000>. The SQLite database is created at `instance/dietmate.db`; the starter catalog is inserted on first launch. Set `DIETMATE_SECRET_KEY` before deploying.

## Current scope

Phase 1 establishes Flask configuration, SQLAlchemy models and database initialization. The dashboard provides the DietMate shell and personalized meal suggestions. Account flows are available at `/auth/register` and `/auth/login`; profile and password settings require login. The food catalog at `/foods/` includes seeded foods plus account-owned food and recipe CRUD. Recipe details and favorites are available through `/recipes/<food_id>`. The adaptive planner lives at `/planner/`: it uses profile-derived energy estimates (or a labeled 1,800 kcal baseline), splits energy as 25/10/30/10/25 across five meals, filters available foods by dietary preference and listed allergies/restrictions, and records the reason for each generated suggestion. User plans are private. Nutrition logging, daily macro totals, weekly calorie trends and CSV export are available at `/nutrition/`. Water intake, custom daily goals, preserved reset history, and weekly intake trends are available at `/water/`. Shopping lists at `/shopping/` support manual management, purchased/pending filters, ingredient generation from saved plans, and CSV export. The calendar at `/calendar/` provides month/week browsing and plan copying. Reports at `/reports/` provide daily, weekly and monthly summaries with CSV export. In-app reminders and reminder preferences are available at `/notifications/` and `/settings/`; reminders are checked when the notification center is opened. Nutrition, hydration and BMI figures are estimates, not medical advice.
