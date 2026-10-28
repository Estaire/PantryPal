import json
import logging
from collections import Counter
from contextlib import asynccontextmanager

import httpx
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.database import Base, engine
from app.models import User
from app.routes.auth import router as auth_router
from app.pantry_models import PantryIngredient
from app.routes.pantry import router as pantry_router
from app.routes.saved_recipes import router as saved_recipes_router

from app.services.recommendations import (
    calculate_substitution_score,
    find_assumed_staples,
    find_available_substitutions,
    find_missing_ingredients,
    find_substitutes,
    get_recipe_status,
    get_recommendation_category,
    normalize_ingredient,
    rank_recipe,
    get_substitution_details,
)

from app.services.recipe_providers.themealdb import (
    close_client,
    get_recipe_by_id,
    search_full_recipes,
    warm_catalog,
)


logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 12
MAX_PAGE_SIZE = 100

# Ranked results per pantry. Scoring every matching recipe is cheap but not
# free, and pagination means the same pantry is requested once per page.
# Caching keeps page 2, 3, ... to a list slice and keeps ordering stable
# while the user scrolls.
RANKING_CACHE_TTL = 300  # seconds
ranking_cache = TTLCache(maxsize=32, ttl=RANKING_CACHE_TTL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload the recipe catalog on startup and close the HTTP client on shutdown."""
    Base.metadata.create_all(bind=engine)

    try:
        await warm_catalog()
    except Exception:
        # Don't block startup if TheMealDB is unreachable or rate limiting us;
        # the catalog will be loaded on the first search instead.
        logger.warning(
            "Could not preload the recipe catalog; it will load on first search.",
            exc_info=True,
        )

    yield

    await close_client()


app = FastAPI(title="PantryPal API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(pantry_router)   
app.include_router(saved_recipes_router)
app.add_middleware(GZipMiddleware, minimum_size=1000)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.0.9:5173/",
    ],
    allow_origin_regex=r"http://(192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    """Confirm that the API is running."""
    return {"status": "ok"}


def normalize_pantry(ingredients):
    """Normalize and de-duplicate pantry ingredients, preserving order."""
    pantry = []
    seen = set()

    for ingredient in ingredients:
        normalized = normalize_ingredient(ingredient)

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        pantry.append(normalized)

    return pantry


def score_recipe(recipe, pantry):
    """
    Validate one provider recipe and score it against the pantry.

    Returns the API representation of the recipe, or None if the record
    is unusable.
    """
    if not isinstance(recipe, dict):
        logger.warning("Skipping a malformed recipe record.")
        return None

    recipe_id = recipe.get("id")
    name = recipe.get("name")
    raw_ingredients = recipe.get("ingredients")

    if (
        recipe_id is None
        or not str(recipe_id).strip()
        or not isinstance(name, str)
        or not name.strip()
        or not isinstance(raw_ingredients, list)
    ):
        logger.warning("Skipping a recipe with missing required fields.")
        return None

    normalized_id = str(recipe_id).strip()

    recipe_ingredients = []
    required = []  # canonical names; every matching output uses these

    for ingredient in raw_ingredients:
        if isinstance(ingredient, str) and ingredient.strip():
            ingredient_name = ingredient.strip()
            measure = ""
        elif isinstance(ingredient, dict):
            ingredient_name = ingredient.get("name")
            measure = ingredient.get("measure", "")

            if not isinstance(ingredient_name, str) or not ingredient_name.strip():
                continue

            ingredient_name = ingredient_name.strip()
            measure = measure.strip() if isinstance(measure, str) else ""
        else:
            continue

        canonical = normalize_ingredient(ingredient_name)
        if not canonical:
            continue

        recipe_ingredients.append(
            {
                "name": ingredient_name,
                "measure": measure,
                "canonical": canonical,
            }
        )
        required.append(canonical)

    if not required:
        logger.warning(
            "Skipping recipe %s because it has no usable ingredients.",
            normalized_id,
        )
        return None

    missing = find_missing_ingredients(pantry, required)
    available_substitutions = find_available_substitutions(pantry, required)
    substitutes = find_substitutes(missing)

    substitution_details = {
        ingredient: get_substitution_details(ingredient)
        for ingredient in set(missing) | set(available_substitutions)
    }

    return {
        "id": normalized_id,
        "name": name.strip(),
        "image": recipe["image"] if isinstance(recipe.get("image"), str) else "",
        "ingredients": recipe_ingredients,
        "instructions": (
            recipe["instructions"]
            if isinstance(recipe.get("instructions"), str)
            else ""
        ),
        "match_score": calculate_substitution_score(pantry, required),
        "missing_ingredients": missing,
        "status": get_recipe_status(missing),
        "substitutions": substitutes,
        "substitution_details": substitution_details,
        "missing_count": len(missing),
        "recommendation_category": get_recommendation_category(
            pantry,
            missing,
            substitutes,
            required=required,
        ),
        "available_substitutions": available_substitutions,
        "assumed_staples": find_assumed_staples(required),
    }

async def get_ranked_recipes(pantry):
    """Return every matching recipe, scored and ranked (cached per pantry)."""
    cache_key = tuple(sorted(pantry))
    cached = ranking_cache.get(cache_key)

    if cached is not None:
        return cached

    try:
        recipes = await search_full_recipes(pantry)
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("Recipe provider request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The recipe provider is temporarily unavailable.",
        ) from exc

    if not isinstance(recipes, list):
        logger.error("Recipe provider returned an unexpected result type.")
        raise HTTPException(
            status_code=502,
            detail="The recipe provider returned an invalid response.",
        )

    ranked = []
    seen_ids = set()

    for recipe in recipes:
        scored = score_recipe(recipe, pantry)

        if scored is None or scored["id"] in seen_ids:
            continue

        seen_ids.add(scored["id"])
        ranked.append(scored)

    ranked.sort(key=rank_recipe)

    result = {
        "recipes": ranked,
        "counts": dict(
            Counter(recipe["recommendation_category"] for recipe in ranked)
        ),
    }

    ranking_cache[cache_key] = result

    return result


@app.get("/api/v1/recipes")
async def get_recipes(
    ingredients: list[str] = Query(...),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
):
    """Return one page of recipes ranked by pantry compatibility."""
    pantry = normalize_pantry(ingredients)

    if not pantry:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one valid ingredient.",
        )

    ranked = await get_ranked_recipes(pantry)
    recipes = ranked["recipes"]
    page = recipes[offset:offset + limit]

    return {
        "recipes": page,
        "pantry": pantry,
        "total": len(recipes),
        "offset": offset,
        "limit": limit,
        "has_more": offset + len(page) < len(recipes),
        "counts": ranked["counts"],
    }


@app.get("/api/v1/recipes/{recipe_id}")
async def get_recipe(
    recipe_id: str,
    ingredients: list[str] = Query(default=[]),
):
    """
    Return a single recipe scored against the given pantry.

    Works even for recipes that share no ingredients with the pantry, so the
    detail panel can keep updating after the user changes their pantry.
    """
    pantry = normalize_pantry(ingredients)

    try:
        recipe = await get_recipe_by_id(recipe_id)
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("Recipe provider request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The recipe provider is temporarily unavailable.",
        ) from exc

    scored = score_recipe(recipe, pantry) if recipe is not None else None

    if scored is None:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    return scored