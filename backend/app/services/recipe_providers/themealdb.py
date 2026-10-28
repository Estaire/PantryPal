"""
TheMealDB client for the recipe recommendation backend.

Instead of calling TheMealDB once per pantry ingredient (and once more per
candidate recipe), this module downloads the whole recipe catalog once with
search.php?f=a ... f=z (26 requests), keeps it in memory for 24 hours, and
matches the user's pantry against it locally.

Result:
- A search makes ZERO upstream requests once the catalog is loaded.
- Pantry size no longer matters (1 ingredient or 200 costs the same).
- Upstream traffic is ~26 requests per day, regardless of users.

Matching works on canonical ingredient names (see recommendations.py), so
"Tomatoes" matches "tomato" and "Chicken Breast" matches "chicken". Assumed
staples (salt, pepper, water, basic oils) are ignored for matching.

This module only decides which recipes are RELEVANT candidates. Scoring,
categorizing and ranking happen in recommendations.py / the router, so there
is a single source of truth for ordering.

Every upstream request goes through one choke point (_get_json) that
enforces a global concurrency cap and retries on 429 / 5xx with backoff.

Requires Python 3.10+ (module-level asyncio primitives).
"""

import asyncio
import logging
import string
import time
from copy import deepcopy

import httpx
from cachetools import TTLCache

from app.services.recommendations import (
    STAPLES,
    expand_with_substitutes,
    normalize_ingredient,
)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# Swap "1" for your personal key once you have one (ideally from an env var).
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

MAX_CONCURRENT_REQUESTS = 3  # global cap across all upstream calls
REQUEST_TIMEOUT = 10.0
MAX_RETRIES = 4
MAX_BACKOFF_SECONDS = 30.0
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

CATALOG_LETTERS = string.ascii_lowercase
CATALOG_TTL = 24 * 3600  # refresh the catalog once a day
CATALOG_RETRY_COOLDOWN = 60.0  # wait before retrying letters that failed


logger = logging.getLogger(__name__)

_upstream_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
_client = None

# letter -> list of (normalized recipe, frozenset of canonical NON-STAPLE
# ingredient names)
_letter_cache = TTLCache(maxsize=len(CATALOG_LETTERS), ttl=CATALOG_TTL)
_catalog_lock = asyncio.Lock()
_next_retry_at = 0.0
_last_catalog_error = None


# --------------------------------------------------------------------------- #
# HTTP plumbing
# --------------------------------------------------------------------------- #

def _get_client():
    """Return a shared AsyncClient (created lazily inside the running loop)."""
    global _client

    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)

    return _client


async def close_client():
    """Call this from your app's shutdown handler / lifespan."""
    global _client

    if _client is not None and not _client.is_closed:
        await _client.aclose()

    _client = None


def _backoff_delay(response, attempt):
    """Honor Retry-After when present, otherwise use exponential backoff."""
    retry_after = (
        response.headers.get("Retry-After", "")
        if response is not None
        else ""
    )

    try:
        delay = float(retry_after)
    except ValueError:
        delay = 2 ** attempt

    return min(delay, MAX_BACKOFF_SECONDS)


async def _get_json(client, path, params):
    """
    Single choke point for all upstream calls.

    - Global concurrency cap via _upstream_semaphore.
    - Retries 429 / 5xx / transport errors / non-JSON bodies with backoff.
    - Sleeps OUTSIDE the semaphore so waiting requests don't block others.
    """
    last_error = None

    for attempt in range(MAX_RETRIES):
        response = None

        try:
            async with _upstream_semaphore:
                response = await client.get(
                    f"{BASE_URL}/{path}",
                    params=params,
                )

            if response.status_code in RETRYABLE_STATUS_CODES:
                last_error = httpx.HTTPStatusError(
                    f"{response.status_code} from TheMealDB",
                    request=response.request,
                    response=response,
                )
            else:
                response.raise_for_status()
                return response.json()

        except (httpx.TransportError, ValueError) as exc:
            # Timeouts / connection errors / body that isn't valid JSON.
            last_error = exc

        delay = _backoff_delay(response, attempt)
        logger.warning(
            "TheMealDB request %s %r failed (%s); retry %d/%d in %.1fs",
            path,
            params,
            last_error,
            attempt + 1,
            MAX_RETRIES,
            delay,
        )
        await asyncio.sleep(delay)

    raise last_error or httpx.HTTPError("TheMealDB request failed after retries")


# --------------------------------------------------------------------------- #
# Parsing / normalization
# --------------------------------------------------------------------------- #

def extract_ingredients(recipe):
    """Extract ingredient names together with their measurements."""
    if not isinstance(recipe, dict):
        return []

    ingredients = []

    # TheMealDB meals have a fixed set of 20 ingredient/measure slots.
    for number in range(1, 21):
        ingredient = recipe.get(f"strIngredient{number}")

        if not isinstance(ingredient, str) or not ingredient.strip():
            continue

        measure = recipe.get(f"strMeasure{number}")
        measure = measure.strip() if isinstance(measure, str) else ""

        ingredients.append({
            "name": ingredient.strip(),
            "measure": measure,
        })

    return ingredients


def _normalize_recipe(data):
    """Validate a {"meals": [meal]} payload and normalize it, or return None."""
    if not isinstance(data, dict):
        return None

    meals = data.get("meals")

    if not isinstance(meals, list) or not meals:
        return None

    recipe = meals[0]

    if not isinstance(recipe, dict):
        return None

    actual_id = recipe.get("idMeal")
    name = recipe.get("strMeal")

    if not isinstance(actual_id, (str, int)) or not str(actual_id).strip():
        return None

    if not isinstance(name, str) or not name.strip():
        return None

    ingredients = extract_ingredients(recipe)

    if not ingredients:
        logger.warning(
            "Skipping recipe %r because it has no ingredients",
            actual_id,
        )
        return None

    image = recipe.get("strMealThumb")
    instructions = recipe.get("strInstructions")
    
    
    return {
        "id": str(actual_id),
        "name": name.strip(),
        "image": image.strip() if isinstance(image, str) else "",
        "ingredients": ingredients,
        "instructions": (
            instructions.strip()
            if isinstance(instructions, str)
            else ""
        ),
    }


# --------------------------------------------------------------------------- #
# Catalog loading
# --------------------------------------------------------------------------- #

async def _fetch_letter(client, letter):
    """Fetch every meal whose name starts with `letter`."""
    data = await _get_json(client, "search.php", {"f": letter})
    meals = data.get("meals") if isinstance(data, dict) else None

    entries = []

    # TheMealDB returns null when a letter has no meals.
    for meal in meals if isinstance(meals, list) else []:
        recipe = _normalize_recipe({"meals": [meal]})

        if recipe is None:
            continue

        core = frozenset(
            name
            for name in (
                normalize_ingredient(item["name"])
                for item in recipe["ingredients"]
            )
            if name and name not in STAPLES
        )

        # A recipe made only of staples can never be a relevant match.
        if core:
            entries.append((recipe, core))

    return entries


async def ensure_catalog():
    """
    Make sure the catalog is loaded, fetching only letters that are missing.

    - Concurrent callers share one load (the lock).
    - If some letters fail, the rest of the catalog is still used and the
      failed letters are retried after a short cooldown.
    - During the cooldown, requests fail fast instead of retrying upstream.
    - If NOTHING could be loaded, the first error is raised.
    """
    global _next_retry_at, _last_catalog_error

    async with _catalog_lock:
        missing = [
            letter for letter in CATALOG_LETTERS
            if letter not in _letter_cache
        ]

        if not missing:
            return

        # Cooldown after a failed load: don't hammer the API (or make every
        # request wait through the full retry/backoff cycle).
        if time.monotonic() < _next_retry_at:
            if _letter_cache:
                return  # degraded: serve the letters we do have

            raise _last_catalog_error  # nothing to serve: fail fast

        client = _get_client()

        results = await asyncio.gather(
            *(_fetch_letter(client, letter) for letter in missing),
            return_exceptions=True,
        )

        errors = []

        for letter, result in zip(missing, results):
            if isinstance(result, Exception):
                errors.append(result)
                logger.debug(
                    "Failed to load catalog letter %r: %s",
                    letter,
                    result,
                )
            else:
                _letter_cache[letter] = result

        if errors:
            _next_retry_at = time.monotonic() + CATALOG_RETRY_COOLDOWN
            _last_catalog_error = errors[0]

            logger.warning(
                "Failed to load %d of %d catalog letters (first error: %s); "
                "retrying in %.0fs",
                len(errors),
                len(missing),
                errors[0],
                CATALOG_RETRY_COOLDOWN,
            )

            if not _letter_cache:
                raise errors[0]
        else:
            logger.info("Loaded TheMealDB catalog with %d recipes", catalog_size())


def _iter_catalog():
    """Yield (recipe, canonical non-staple ingredient set) for every recipe."""
    seen_ids = set()

    for letter in CATALOG_LETTERS:
        for recipe, core in _letter_cache.get(letter) or []:
            if recipe["id"] not in seen_ids:
                seen_ids.add(recipe["id"])
                yield recipe, core


def catalog_size():
    """Number of recipes currently loaded (handy for sanity checks)."""
    return sum(1 for _ in _iter_catalog())


async def warm_catalog():
    """Call from your startup handler so the first search is instant."""
    await ensure_catalog()


# --------------------------------------------------------------------------- #
# Public entry points
# --------------------------------------------------------------------------- #

async def search_full_recipes(ingredients):
    """
    Return the recipes relevant to a pantry, in no particular order.

    The number of matches a recipe needs scales with the size of the pantry:
    one match for pantries of up to five non-staple ingredients, and roughly
    one more for every three ingredients after that. Known substitutes count
    as matches, so soy milk makes milk recipes relevant. A recipe with fewer
    matches than that is still returned if it shares at least one ingredient
    with a pantry of one or two items.

    Staples are ignored on both sides, so a pantry of just "salt" matches
    nothing.

    Makes no upstream calls once the catalog is loaded. Ranking is done by
    the caller.
    """
    pantry_core = sorted(
        {
            normalized
            for normalized in (
                normalize_ingredient(ingredient)
                for ingredient in ingredients
            )
            if normalized and normalized not in STAPLES
        }
    )

    if not pantry_core:
        return []

    pantry = set(expand_with_substitutes(pantry_core))
    required_matches = max(1, len(pantry_core) // 3)

    await ensure_catalog()

    results = []

    for recipe, core in _iter_catalog():
        matched = len(core & pantry)

        if matched >= max(1, min(required_matches, len(core))):
            results.append(recipe)

    return deepcopy(results)


async def get_recipe_by_id(recipe_id):
    """
    Return one normalized recipe from the catalog, or None if unknown.

    Unlike search_full_recipes, this does not require the recipe to share
    any ingredient with a pantry.
    """
    await ensure_catalog()

    wanted = str(recipe_id).strip()

    for recipe, _ in _iter_catalog():
        if recipe["id"] == wanted:
            return deepcopy(recipe)

    return None