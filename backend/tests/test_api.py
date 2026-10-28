import os
import tempfile
from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models import User
from app.pantry_models import PantryIngredient

_test_dir = tempfile.mkdtemp()
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-0123456789abcdef0123456789")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_test_dir, 'test.db')}"

import pytest
from fastapi.testclient import TestClient

import app.main as app_main
from app.database import Base, engine
from app.main import app, ranking_cache
from app.saved_recipe_models import SavedRecipe  # noqa: F401  (registers the table)


SAVE_BODY = {
    "name": "Chicken Fried Rice",
    "image": "https://example.com/rice.jpg",
    "ingredients": [
        {"name": "chicken breast", "measure": "200g"},
        {"name": "rice", "measure": "1 cup"},
    ],
    "instructions": "Cook the rice. Add the chicken.",
}


def fake_recipe(recipe_id, name, ingredients):
    return {
        "id": recipe_id,
        "name": name,
        "image": "",
        "ingredients": [{"name": item, "measure": "1"} for item in ingredients],
        "instructions": "Cook.",
    }


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ranking_cache.clear()

    # No `with` block, so the lifespan (which warms the TheMealDB catalog
    # over the network) doesn't run. Tables are created above instead.
    return TestClient(app)


def auth_headers(client, email="cook@example.com"):
    password = "correct-horse-battery"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


# --------------------------------------------------------------------------- #
# Health and recipe search
# --------------------------------------------------------------------------- #

def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recipes_rejects_blank_pantry(client):
    response = client.get("/api/v1/recipes", params={"ingredients": ""})

    assert response.status_code == 400


def test_recipes_pagination_and_caching(client, monkeypatch):
    calls = {"count": 0}
    recipes = [
        fake_recipe("1", "One", ["chicken"]),
        fake_recipe("2", "Two", ["chicken"]),
        fake_recipe("3", "Three", ["chicken"]),
    ]

    async def fake_search(pantry):
        calls["count"] += 1
        return recipes

    monkeypatch.setattr(app_main, "search_full_recipes", fake_search)

    first = client.get(
        "/api/v1/recipes",
        params={"ingredients": "chicken", "limit": 2, "offset": 0},
    ).json()
    second = client.get(
        "/api/v1/recipes",
        params={"ingredients": "chicken", "limit": 2, "offset": 2},
    ).json()

    assert first["total"] == 3
    assert len(first["recipes"]) == 2
    assert first["has_more"] is True

    assert len(second["recipes"]) == 1
    assert second["has_more"] is False

    # Both pages come from one provider search.
    assert calls["count"] == 1


def test_recipes_are_scored_against_pantry(client, monkeypatch):
    async def fake_search(pantry):
        return [fake_recipe("1", "Chicken Soup", ["chicken", "carrot"])]

    monkeypatch.setattr(app_main, "search_full_recipes", fake_search)

    data = client.get(
        "/api/v1/recipes",
        params={"ingredients": "chicken"},
    ).json()

    recipe = data["recipes"][0]
    assert recipe["id"] == "1"
    assert recipe["missing_ingredients"] == ["carrot"]
    assert 0 < recipe["match_score"] < 100


def test_recipe_detail_returns_canonical_ingredients(client, monkeypatch):
    async def fake_get(recipe_id):
        return fake_recipe("52818", "Chicken Dish", ["Chicken Breast"])

    monkeypatch.setattr(app_main, "get_recipe_by_id", fake_get)

    data = client.get(
        "/api/v1/recipes/52818",
        params={"ingredients": "chicken"},
    ).json()

    assert data["ingredients"][0]["canonical"] == "chicken"
    assert data["match_score"] == 100.0
    assert data["missing_ingredients"] == []


def test_recipe_detail_404_for_unknown_id(client, monkeypatch):
    async def fake_get(recipe_id):
        return None

    monkeypatch.setattr(app_main, "get_recipe_by_id", fake_get)

    response = client.get("/api/v1/recipes/does-not-exist")

    assert response.status_code == 404


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #

def test_register_then_login(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "correct-horse-battery"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "new@example.com", "password": "correct-horse-battery"},
    )

    assert register.status_code == 201
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_register_duplicate_email_conflicts(client):
    body = {"email": "dup@example.com", "password": "correct-horse-battery"}

    client.post("/api/v1/auth/register", json=body)
    response = client.post("/api/v1/auth/register", json=body)

    assert response.status_code == 409


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "correct-horse-battery"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "wrong-password-here"},
    )

    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")

    # HTTPBearer returns 403 on some FastAPI versions and 401 on others.
    assert response.status_code in (401, 403)


# --------------------------------------------------------------------------- #
# Pantry
# --------------------------------------------------------------------------- #

def test_pantry_requires_auth(client):
    response = client.get("/api/v1/pantry")

    assert response.status_code in (401, 403)


def test_pantry_saves_canonical_names(client):
    headers = auth_headers(client)

    saved = client.put(
        "/api/v1/pantry",
        json={"ingredients": ["Chicken Breast", "chicken", "Eggs", "  "]},
        headers=headers,
    ).json()
    loaded = client.get("/api/v1/pantry", headers=headers).json()

    assert saved["ingredients"] == ["chicken", "egg"]
    assert loaded["ingredients"] == ["chicken", "egg"]


def test_pantry_is_scoped_to_user(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")

    client.put("/api/v1/pantry", json={"ingredients": ["rice"]}, headers=alice)

    response = client.get("/api/v1/pantry", headers=bob).json()
    assert response["ingredients"] == []


# --------------------------------------------------------------------------- #
# Saved recipes
# --------------------------------------------------------------------------- #

def test_saved_recipe_lifecycle(client):
    headers = auth_headers(client)
    url = "/api/v1/saved-recipes/52818"

    first = client.put(url, json=SAVE_BODY, headers=headers)
    assert first.status_code == 201
    assert first.json()["id"] == "52818"

    # Saving again is idempotent and keeps the original snapshot.
    second = client.put(url, json={**SAVE_BODY, "name": "Changed"}, headers=headers)
    assert second.status_code == 200
    assert second.json()["name"] == "Chicken Fried Rice"

    listing = client.get("/api/v1/saved-recipes", headers=headers).json()
    assert [item["id"] for item in listing] == ["52818"]

    assert client.delete(url, headers=headers).status_code == 204
    assert client.delete(url, headers=headers).status_code == 404
    assert client.get("/api/v1/saved-recipes", headers=headers).json() == []


def test_saved_recipes_are_scoped_to_user(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")

    client.put("/api/v1/saved-recipes/1", json=SAVE_BODY, headers=alice)

    assert client.get("/api/v1/saved-recipes", headers=bob).json() == []
    assert client.delete("/api/v1/saved-recipes/1", headers=bob).status_code == 404


def test_saved_recipe_rejects_overlong_id(client):
    headers = auth_headers(client)

    response = client.put(
        f"/api/v1/saved-recipes/{'x' * 65}",
        json=SAVE_BODY,
        headers=headers,
    )

    assert response.status_code == 422


# --------------------------------------------------------------------------- #
# Contract: recipes response includes the canonical pantry
# --------------------------------------------------------------------------- #

def test_recipes_response_includes_canonical_pantry(client, monkeypatch):
    async def fake_search(pantry):
        return []

    monkeypatch.setattr(app_main, "search_full_recipes", fake_search)

    data = client.get(
        "/api/v1/recipes",
        params={"ingredients": ["Chicken Breast", "rice"]},
    ).json()

    assert data["pantry"] == ["chicken", "rice"]


# --------------------------------------------------------------------------- #
# Saved recipes: round trip keeps ingredients intact
# --------------------------------------------------------------------------- #

def test_saved_recipe_round_trip_preserves_ingredients(client):
    headers = auth_headers(client)

    client.put("/api/v1/saved-recipes/52818", json=SAVE_BODY, headers=headers)
    listing = client.get("/api/v1/saved-recipes", headers=headers).json()

    assert listing[0]["ingredients"] == SAVE_BODY["ingredients"]
    assert listing[0]["instructions"] == SAVE_BODY["instructions"]


# --------------------------------------------------------------------------- #
# Pantry: legacy rows are canonicalized on read
# --------------------------------------------------------------------------- #

def test_pantry_canonicalizes_legacy_rows(client):
    headers = auth_headers(client, "legacy@example.com")

    # Simulate a row saved before canonicalization existed.
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "legacy@example.com"))
        db.add(PantryIngredient(user_id=user.id, ingredient="Chicken Breast"))
        db.commit()

    loaded = client.get("/api/v1/pantry", headers=headers).json()

    assert loaded["ingredients"] == ["chicken"]


# --------------------------------------------------------------------------- #
# Auth edge cases
# --------------------------------------------------------------------------- #

def test_malformed_token_is_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_token_for_deleted_user_is_rejected(client):
    from app.auth import create_access_token

    # A well-formed token whose user does not exist.
    token = create_access_token(999_999)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# --------------------------------------------------------------------------- #
# Database: deleting a user cascades to their data.
# This verifies the SQLite foreign key pragma in database.py.
# --------------------------------------------------------------------------- #

def test_deleting_user_cascades_to_pantry_and_saved_recipes(client):
    headers = auth_headers(client, "gone@example.com")

    client.put("/api/v1/pantry", json={"ingredients": ["rice"]}, headers=headers)
    client.put("/api/v1/saved-recipes/1", json=SAVE_BODY, headers=headers)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "gone@example.com"))
        user_id = user.id

        db.execute(delete(User).where(User.id == user_id))
        db.commit()

        pantry_rows = db.scalar(
            select(func.count())
            .select_from(PantryIngredient)
            .where(PantryIngredient.user_id == user_id)
        )
        saved_rows = db.scalar(
            select(func.count())
            .select_from(SavedRecipe)
            .where(SavedRecipe.user_id == user_id)
        )

    assert pantry_rows == 0
    assert saved_rows == 0