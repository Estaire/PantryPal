# PantryPal

Find recipes you can make with what's already in your kitchen. PantryPal ranks recipes by how well they match your pantry, suggests substitutions for missing ingredients, and lets you save recipes to revisit later.

**Live demo:** [pantrypal.vercel.app](https://pantrypal.vercel.app)

![PantryPal search and recipe view](docs/demo.gif)

## Features

- Search recipes by the ingredients you have, ranked by match
- Sort results into "Ready to cook," "Almost there," and "More ingredients needed"
- Suggested substitutions, with quality notes for each
- Accounts with a pantry that syncs across devices
- Save recipes and revisit them later
- Responsive layout for phones and desktops

## Tech stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Vitest
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, pytest
- **Auth:** JWT access tokens with Argon2 password hashing
- **Data:** TheMealDB recipe catalog, cached in memory
- **Hosting:** Vercel (frontend), Railway (backend)

## How it works

[Two or three sentences per point. Suggested points below.]

- **Catalog caching:** The backend loads TheMealDB's catalog once a day and matches pantries locally, so a search makes no upstream requests.
- **Stable saved recipes:** Saved recipes store only recipe details, not match scores. Opening a saved recipe re-scores it against your current pantry.
- **Ingredient normalization:** The backend maps variants like "chicken breast" and "eggs" to canonical names, so your pantry and recipes always compare correctly.

## Run it locally

### Backend

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then set JWT_SECRET_KEY
export $(cat .env | xargs)       # or set the variables in your shell
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.development
npm run dev
```

Open http://localhost:5173.

## Tests

```bash
cd backend && python -m pytest -q
cd frontend && npm test
```

## Project structure

```
backend/    FastAPI app, recommendation logic, tests
frontend/   React app, components, hooks, tests
```

## Known limitations

- The free hosting tier sleeps when idle, so the first request can take 30 seconds.
- Recipe data comes from TheMealDB and is limited to its catalog.
- SQLite runs as a single instance, so the backend can't scale horizontally.

