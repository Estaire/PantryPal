"""
Ingredient normalization, matching and scoring.

What changed compared with the original version:

1. Canonical ingredient names. `normalize_ingredient` now strips accents,
   punctuation and preparation words ("finely chopped"), singularizes the
   last word ("eggs" -> "egg", "tomatoes" -> "tomato") and maps known
   variants to one name ("chicken breast" -> "chicken", "scallion" ->
   "spring onion"). Both the pantry and the recipes go through the same
   function, so "Tomatoes" in a recipe matches "tomato" in the pantry.

2. Staples (salt, pepper, water, basic oils) are assumed to be available.
   They are never "missing", and they don't count toward match scores or
   relevance.

3. Categories are size-aware and weighted. A 3-ingredient recipe missing one
   thing is "almost there"; a 14-ingredient recipe can miss up to three.
   Missing a main ingredient (chicken, rice, ...) counts double.

4. Ranking uses the same weighted missing count, so missing the chicken ranks
   below missing the parsley.

Everything that used to be public still exists with the same name. The only
signature change is an optional `required=` argument on
`get_recommendation_category`.
"""

import re
import unicodedata
from functools import lru_cache

from app.services.substitutions import (
    GREAT,
    GOOD,
    FAIR,
    SUBSTITUTION_RULES,
    DIET_VEGAN,
    DIET_VEGETARIAN_ONLY,
    DIET_GLUTEN_FREE,
    DIET_NUT_FREE,
)


# Preparation / size words that don't change which ingredient it is.
MODIFIER_WORDS = frozenset({
    "fresh", "freshly", "large", "small", "medium", "big", "organic",
    "chopped", "sliced", "diced", "grated", "peeled", "tinned", "canned",
    "raw", "finely", "roughly", "thinly", "ripe",
})

# Plurals the generic rules would get wrong (or singulars ending in "s").
PLURAL_EXCEPTIONS = {
    "leaves": "leaf", "loaves": "loaf", "halves": "half",
    "cookies": "cookie", "brownies": "brownie", "pies": "pie",
    "smoothies": "smoothie", "veggies": "veggie",
    "chillies": "chilli", "chilies": "chili", "quiches": "quiche",
    "molasses": "molasses",
}

# canonical name -> variants that mean (close enough to) the same thing.
# Keys and variants are normalized automatically, so plural/singular and
# capitalization don't matter when adding entries.
ALIAS_GROUPS = {
    # Meat and fish
    "chicken": [
        "chicken breast", "chicken thigh", "chicken leg", "chicken wing",
        "chicken drumstick", "chicken fillet", "whole chicken",
        "boneless chicken", "skinless chicken breast",
        "boneless skinless chicken breast",
    ],
    "beef": ["stewing beef", "braising beef", "diced beef", "beef steak"],
    "ground beef": [
        "minced beef", "beef mince", "mince beef", "lean ground beef",
        "lean minced beef",
    ],
    "ground pork": ["minced pork", "pork mince"],
    "ground lamb": ["minced lamb", "lamb mince"],
    "ground turkey": ["minced turkey", "turkey mince"],
    "pork": [
        "pork shoulder", "pork chop", "pork loin", "pork tenderloin",
        "pork fillet", "diced pork",
    ],
    "lamb": [
        "lamb shoulder", "lamb leg", "leg of lamb", "diced lamb",
        "lamb chop", "lamb fillet",
    ],
    "bacon": [
        "streaky bacon", "back bacon", "smoked bacon", "bacon rasher",
        "bacon strip",
    ],
    "sausage": [
        "pork sausage", "beef sausage", "chipolata", "cumberland sausage",
    ],
    "shrimp": [
        "prawn", "king prawn", "tiger prawn", "jumbo prawn", "jumbo shrimp",
    ],
    "salmon": ["salmon fillet"],
    "cod": ["cod fillet"],

    # Vegetables and herbs
    "onion": [
        "red onion", "white onion", "yellow onion", "brown onion",
        "sweet onion",
    ],
    "spring onion": ["scallion", "green onion", "salad onion"],
    "garlic": [
        "garlic clove", "minced garlic", "crushed garlic", "garlic bulb",
        "clove of garlic",
    ],
    "ginger": ["root ginger", "ginger root"],
    "tomato": [
        "cherry tomato", "plum tomato", "vine tomato", "beef tomato",
        "crushed tomato",
    ],
    "tomato paste": ["tomato puree", "concentrated tomato puree"],
    "potato": [
        "new potato", "baby potato", "white potato", "floury potato",
        "waxy potato", "russet potato", "maris piper potato",
    ],
    "eggplant": ["aubergine"],
    "zucchini": ["courgette"],
    "bell pepper": [
        "capsicum", "sweet pepper", "red pepper", "green pepper",
        "yellow pepper", "orange pepper", "red bell pepper",
        "green bell pepper", "yellow bell pepper", "orange bell pepper",
    ],
    "chilli": [
        "chili", "chile", "red chilli", "green chilli", "red chili",
        "green chili", "chilli pepper", "chili pepper",
    ],
    "chilli powder": ["chili powder"],
    "chilli flake": ["chili flake", "red pepper flake", "crushed red pepper"],
    "mushroom": [
        "button mushroom", "chestnut mushroom", "cremini mushroom",
        "white mushroom", "closed cup mushroom",
    ],
    "celery": ["celery stick", "celery stalk", "celery rib"],
    "carrot": ["baby carrot"],
    "pea": ["green pea", "frozen pea", "petits pois", "garden pea"],
    "chickpea": ["garbanzo bean", "garbanzo", "chick pea"],
    "apple": [
        "cooking apple", "eating apple", "bramley apple", "granny smith apple",
    ],
    "coriander": [
        "cilantro", "coriander leaf", "cilantro leaf",
    ],
    "parsley": [
        "flat leaf parsley", "flatleaf parsley", "curly parsley",
        "italian parsley", "parsley leaf", "dried parsley",
    ],
    "basil": ["basil leaf", "dried basil"],
    "thyme": ["thyme leaf", "thyme sprig", "dried thyme"],
    "rosemary": ["rosemary sprig", "dried rosemary"],
    "mint": ["mint leaf", "dried mint"],
    "oregano": ["dried oregano"],
    "sage": ["dried sage"],
    "dill": ["dill sprig", "dried dill"],
    "tarragon": ["dried tarragon"],

    # Dairy and eggs
    "egg": ["free range egg"],
    "butter": [
        "unsalted butter", "salted butter", "melted butter",
        "softened butter", "cold butter",
    ],
    "milk": [
        "whole milk", "full fat milk", "semi skimmed milk", "skimmed milk",
        "skim milk", "low fat milk",
    ],
    "soy milk": ["soya milk"],
    "heavy cream": [
        "double cream", "whipping cream", "thickened cream",
        "heavy whipping cream",
    ],
    "sour cream": ["soured cream"],
    "yogurt": [
        "yoghurt", "greek yogurt", "greek yoghurt", "natural yogurt",
        "natural yoghurt", "plain yogurt", "plain yoghurt",
        "greek style yogurt",
    ],
    "cheddar": [
        "cheddar cheese", "mature cheddar", "mature cheddar cheese",
        "mild cheddar", "sharp cheddar", "extra mature cheddar",
    ],
    "parmesan": ["parmesan cheese", "parmigiano reggiano", "parmigiano"],
    "mozzarella": ["mozzarella cheese", "mozzarella ball", "buffalo mozzarella"],
    "feta": ["feta cheese"],

    # Pantry goods
    "flour": ["plain flour", "all purpose flour", "white flour"],
    "self raising flour": ["self rising flour"],
    "wholemeal flour": ["whole wheat flour", "wholewheat flour"],
    "bread flour": ["strong flour", "strong white flour", "strong bread flour"],
    "cornstarch": ["cornflour", "corn flour", "corn starch"],
    "sugar": [
        "caster sugar", "granulated sugar", "white sugar", "superfine sugar",
        "white caster sugar",
    ],
    "icing sugar": ["powdered sugar", "confectioners sugar", "confectioner sugar"],
    "brown sugar": [
        "light brown sugar", "dark brown sugar", "soft brown sugar",
        "light brown soft sugar", "dark brown soft sugar", "muscovado sugar",
        "demerara sugar",
    ],
    "rice": [
        "long grain rice", "white rice", "basmati rice", "jasmine rice",
        "long grain white rice", "easy cook rice",
    ],
    "pasta": [
        "spaghetti", "penne", "fusilli", "macaroni", "tagliatelle",
        "linguine", "rigatoni", "farfalle", "fettuccine", "dried pasta",
        "pasta shell",
    ],
    "oat": ["rolled oat", "porridge oat", "jumbo oat"],
    "breadcrumb": [
        "panko", "panko breadcrumb", "dried breadcrumb", "fresh breadcrumb",
    ],
    "bread": ["white bread", "sliced bread"],
    "baking soda": [
        "bicarbonate of soda", "bicarbonate soda", "bicarb",
        "sodium bicarbonate",
    ],
    "vanilla extract": ["vanilla essence"],
    "honey": ["clear honey", "runny honey"],
    "peanut butter": ["smooth peanut butter", "crunchy peanut butter"],
    "mayonnaise": ["mayo"],
    "ketchup": ["tomato ketchup", "catsup"],
    "soy sauce": [
        "light soy sauce", "dark soy sauce", "soya sauce",
        "low sodium soy sauce",
    ],
    "chicken stock": [
        "chicken broth", "chicken bouillon", "chicken stock cube",
        "chicken bouillon cube", "chicken stock powder", "chicken stock pot",
    ],
    "beef stock": [
        "beef broth", "beef bouillon", "beef stock cube",
        "beef bouillon cube", "beef stock powder", "beef stock pot",
    ],
    "vegetable stock": [
        "vegetable broth", "vegetable bouillon", "vegetable stock cube",
        "vegetable bouillon cube", "vegetable stock powder",
        "vegetable stock pot",
    ],

    # Staples (assumed available, see STAPLE_INGREDIENTS)
    "salt": [
        "sea salt", "table salt", "kosher salt", "flaky salt", "rock salt",
        "fine salt", "coarse salt",
    ],
    "black pepper": [
        "pepper", "ground black pepper", "cracked black pepper",
        "white pepper", "ground pepper", "black peppercorn", "peppercorn",
    ],
    "water": [
        "cold water", "warm water", "hot water", "boiling water", "ice water",
        "iced water", "tap water",
    ],
    "vegetable oil": [
        "sunflower oil", "canola oil", "rapeseed oil", "cooking oil",
        "corn oil", "oil",
    ],
    "olive oil": [
        "extra virgin olive oil", "virgin olive oil", "light olive oil",
    ],
}

# Assumed to be in every kitchen: never "missing", ignored for scoring.
STAPLE_INGREDIENTS = ["salt", "black pepper", "water", "vegetable oil", "olive oil"]

# Main ingredients: missing one weighs double.
MAJOR_INGREDIENT_NAMES = [
    "chicken", "beef", "ground beef", "pork", "ground pork", "lamb",
    "ground lamb", "turkey", "ground turkey", "fish", "salmon", "cod", "tuna",
    "shrimp", "tofu", "sausage", "rice", "pasta", "potato", "eggs",
]

# Size-aware "almost there": (max recipe size, max weighted missing).
# Recipes larger than the last size allow ALMOST_THERE_DEFAULT_LIMIT.
ALMOST_THERE_LIMITS = ((5, 1), (10, 2))
ALMOST_THERE_DEFAULT_LIMIT = 3


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def _singularize(word):
    """Conservative singularization of a single lowercase word."""
    if word in PLURAL_EXCEPTIONS:
        return PLURAL_EXCEPTIONS[word]

    if len(word) <= 3 or not word.endswith("s"):
        return word

    # asparagus, hummus, couscous, watercress, lemongrass, swiss ...
    if word.endswith(("ss", "us", "is")):
        return word

    if word.endswith("ies") and len(word) >= 5:
        return word[:-3] + "y"  # cherries -> cherry

    if word.endswith("oes"):
        return word[:-2]  # tomatoes -> tomato

    if word.endswith(("ches", "shes", "xes", "sses")):
        return word[:-2]  # peaches -> peach

    return word[:-1]  # eggs -> egg, cloves -> clove


def _base_normalize(text):
    """Clean text and singularize, without applying the alias table."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("'", "").replace("\u2019", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)

    words = text.split()
    stripped = [word for word in words if word not in MODIFIER_WORDS]
    words = stripped or words

    if words:
        words[-1] = _singularize(words[-1])

    return " ".join(words)


def _build_aliases():
    aliases = {}

    for canonical, variants in ALIAS_GROUPS.items():
        target = _base_normalize(canonical)

        for variant in variants:
            key = _base_normalize(variant)

            if not key or key == target:
                continue

            if aliases.get(key, target) != target:
                raise ValueError(
                    f"Alias {variant!r} maps to both "
                    f"{aliases[key]!r} and {target!r}"
                )

            aliases[key] = target

    # A target that is itself an alias would make normalization depend on how
    # many times it is applied.
    for key, target in aliases.items():
        if target in aliases:
            raise ValueError(
                f"Alias chain: {key!r} -> {target!r} -> {aliases[target]!r}"
            )

    return aliases


_ALIASES = _build_aliases()


@lru_cache(maxsize=16384)
def _canonical(text):
    base = _base_normalize(text)
    return _ALIASES.get(base, base)


def normalize_ingredient(ingredient: str) -> str:
    """Return the canonical name used for every ingredient comparison."""
    if not isinstance(ingredient, str):
        return ""

    return _canonical(ingredient)


# Normalize rule keys and alternatives once, using this module's canonical names.
_NORMALIZED_SUBSTITUTION_RULES = {}
for _needed, _options in SUBSTITUTION_RULES.items():
    _needed_name = normalize_ingredient(_needed)
    _normalized_options = _NORMALIZED_SUBSTITUTION_RULES.setdefault(_needed_name, [])
    for _alternative, _quality, _note in _options:
        _alternative_name = normalize_ingredient(_alternative)
        if not _alternative_name or _alternative_name == _needed_name:
            continue
        if not any(existing[0] == _alternative_name for existing in _normalized_options):
            _normalized_options.append((_alternative_name, _quality, _note))



# SUBSTITUTIONS exposes the full curated alternative list; quality-aware
# callers should use SUBSTITUTION_RULES or get_substitution_details().
SUBSTITUTIONS = {
    needed: [alternative for alternative, _, _ in options]
    for needed, options in _NORMALIZED_SUBSTITUTION_RULES.items()
}
SUBSTITUTION_CREDIT = 0.75  # legacy constant; GOOD substitutions earn this.

_SUBSTITUTION_CREDITS = {GREAT: 0.90, GOOD: 0.75, FAIR: 0.0}
_USABLE_SUBSTITUTION_QUALITIES = frozenset({GREAT, GOOD})

# alternative -> needed ingredients it can usefully replace (usable qualities only)
_REVERSE_USABLE_SUBSTITUTES = {}
for _needed, _options in _NORMALIZED_SUBSTITUTION_RULES.items():
    for _alternative, _quality, _ in _options:
        if _quality in _USABLE_SUBSTITUTION_QUALITIES:
            _REVERSE_USABLE_SUBSTITUTES.setdefault(_alternative, []).append(_needed)


def expand_with_substitutes(ingredients) -> list:
    """
    Add ingredients that the pantry can stand in for, one level deep.

    If the pantry has soy milk and soy milk is a usable substitute for milk,
    "milk" is added. Substitutes of substitutes are not followed.
    """
    pantry = _unique_ingredients(ingredients)
    expanded = list(pantry)
    seen = set(pantry)

    for ingredient in pantry:  # iterate the original pantry only
        for needed in _REVERSE_USABLE_SUBSTITUTES.get(ingredient, []):
            if needed not in seen:
                seen.add(needed)
                expanded.append(needed)

    return expanded

STAPLES = frozenset(normalize_ingredient(name) for name in STAPLE_INGREDIENTS)
MAJOR_INGREDIENTS = frozenset(
    normalize_ingredient(name) for name in MAJOR_INGREDIENT_NAMES
)


def _unique_ingredients(ingredients):
    """Return normalized, non-empty ingredient names without duplicates."""
    unique = []
    seen = set()

    for ingredient in ingredients:
        normalized = normalize_ingredient(ingredient)

        if normalized and normalized not in seen:
            unique.append(normalized)
            seen.add(normalized)

    return unique


def _core_required(required):
    """Unique canonical required ingredients, excluding assumed staples."""
    return [
        ingredient
        for ingredient in _unique_ingredients(required)
        if ingredient not in STAPLES
    ]


def is_staple(ingredient: str) -> bool:
    """Whether an ingredient is assumed to be available in any kitchen."""
    return normalize_ingredient(ingredient) in STAPLES


def find_assumed_staples(required) -> list:
    """Return the (unique) staples a recipe uses, with their original names."""
    found = []
    seen = set()

    for ingredient in required:
        normalized = normalize_ingredient(ingredient)

        if normalized in STAPLES and normalized not in seen:
            seen.add(normalized)
            found.append(ingredient)

    return found


def get_ingredient_weight(ingredient: str) -> int:
    """Main ingredients (chicken, rice, ...) count double."""
    return 2 if normalize_ingredient(ingredient) in MAJOR_INGREDIENTS else 1


# --------------------------------------------------------------------------- #
# Substitution helpers
# --------------------------------------------------------------------------- #

def get_substitution_map() -> dict:
    """Return all curated alternatives as canonical names (legacy shape)."""
    return {
        needed: [alternative for alternative, _, _ in options]
        for needed, options in _NORMALIZED_SUBSTITUTION_RULES.items()
    }


def get_substitution_details(ingredient: str) -> list:
    """Return curated alternatives with quality and usage notes.

    Each result has ``ingredient``, ``quality``, ``credit`` and ``note``.
    ``fair`` alternatives are suggestions only and do not count as available.
    """
    needed = normalize_ingredient(ingredient)
    return [
        {
            "ingredient": alternative,
            "quality": quality,
            "credit": _SUBSTITUTION_CREDITS[quality],
            "note": note,
            "counts_as_available": quality in _USABLE_SUBSTITUTION_QUALITIES,
        }
        for alternative, quality, note in _NORMALIZED_SUBSTITUTION_RULES.get(needed, [])
    ]


def find_available_substitutions(available, required) -> dict:
    """Map required ingredients to owned great/good substitutes only."""
    available_clean = set(_unique_ingredients(available))
    found = {}
    seen = set()
    for ingredient in required:
        normalized = normalize_ingredient(ingredient)
        if not normalized or normalized in seen or normalized in STAPLES:
            continue
        seen.add(normalized)
        if normalized in available_clean:
            continue
        matching = [
            alternative for alternative, quality, _ in _NORMALIZED_SUBSTITUTION_RULES.get(normalized, [])
            if quality in _USABLE_SUBSTITUTION_QUALITIES and alternative in available_clean
        ]
        if matching:
            found[ingredient] = matching
    return found


def find_missing_ingredients(available, required) -> list:
    """Return required ingredients with no exact match or reliable substitute.

    ``fair`` alternatives are deliberately excluded: they can be shown as
    suggestions, but cannot make a recipe appear ready to cook.
    """
    available_clean = set(_unique_ingredients(available))
    missing = []
    seen = set()
    for ingredient in required:
        normalized = normalize_ingredient(ingredient)
        if not normalized or normalized in seen or normalized in STAPLES:
            continue
        seen.add(normalized)
        if normalized in available_clean:
            continue
        options = _NORMALIZED_SUBSTITUTION_RULES.get(normalized, [])
        if any(alt in available_clean and quality in _USABLE_SUBSTITUTION_QUALITIES
               for alt, quality, _ in options):
            continue
        missing.append(ingredient)
    return missing


def find_substitutes(missing) -> dict:
    """Suggest every curated alternative, including context-dependent ones.

    Keeps the old return shape (ingredient -> list of alternative names).
    Use ``get_substitution_details`` when the UI needs quality and notes.
    """
    suggestions = {}
    seen = set()
    for ingredient in missing:
        normalized = normalize_ingredient(ingredient)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        alternatives = _NORMALIZED_SUBSTITUTION_RULES.get(normalized, [])
        if alternatives:
            suggestions[ingredient] = [alt for alt, _, _ in alternatives]
    return suggestions


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def calculate_substitution_score(available, required) -> float:
    """Weighted match score with quality-based credit for substitutes.

    Exact matches earn 100%; ``great`` alternatives earn 90%; ``good`` earn
    75%; ``fair`` alternatives earn no score and remain suggestions only.
    Staples are ignored, and main ingredients retain double weight.
    """
    available_clean = set(_unique_ingredients(available))
    required_clean = _core_required(required)
    if not required_clean:
        return 0.0

    total_weight = 0.0
    earned_weight = 0.0
    for ingredient in required_clean:
        weight = get_ingredient_weight(ingredient)
        total_weight += weight
        if ingredient in available_clean:
            earned_weight += weight
            continue
        options = _NORMALIZED_SUBSTITUTION_RULES.get(ingredient, [])
        best_credit = max(
            (_SUBSTITUTION_CREDITS[quality] for alternative, quality, _ in options
             if alternative in available_clean),
            default=0.0,
        )
        earned_weight += weight * best_credit

    return round(earned_weight / total_weight * 100, 1)


def get_recipe_status(missing) -> str:
    """Return the basic status based on unresolved missing ingredients."""
    return "ready_to_cook" if not missing else "missing_ingredients"


def _almost_there_limit(recipe_size):
    for max_size, limit in ALMOST_THERE_LIMITS:
        if recipe_size <= max_size:
            return limit

    return ALMOST_THERE_DEFAULT_LIMIT


def get_recommendation_category(
    available,
    missing,
    substitutions=None,
    required=None,
) -> str:
    """
    Categorize a recipe by how much is missing relative to its size.

    Pass `required` (the recipe's ingredient names) for the size-aware rule:
    small recipes tolerate fewer missing ingredients than large ones, and
    main ingredients count double. Without it, the old rule applies (at most
    two missing ingredients is "almost there").
    """
    # `available` and `substitutions` remain for compatibility with callers.
    del available, substitutions

    missing_unique = _unique_ingredients(missing)

    if not missing_unique:
        return "ready_to_cook"

    if required is None:
        return (
            "almost_there"
            if len(missing_unique) <= 2
            else "more_ingredients_needed"
        )

    missing_weight = sum(
        get_ingredient_weight(ingredient) for ingredient in missing_unique
    )
    recipe_size = len(_core_required(required))

    if missing_weight <= _almost_there_limit(recipe_size):
        return "almost_there"

    return "more_ingredients_needed"


def _missing_weight(recipe):
    missing = recipe.get("missing_ingredients")

    if isinstance(missing, list):
        return sum(
            get_ingredient_weight(ingredient)
            for ingredient in _unique_ingredients(missing)
        )

    count = recipe.get("missing_count")

    return count if isinstance(count, (int, float)) else float("inf")


def rank_recipe(recipe) -> tuple:
    """Rank by category, weighted missing, match score, then recipe name."""
    category_priority = {
        "ready_to_cook": 0,
        "almost_there": 1,
        "more_ingredients_needed": 2,
    }

    match_score = recipe.get("match_score", 0)
    name = recipe.get("name", "")

    if not isinstance(match_score, (int, float)):
        match_score = 0

    if not isinstance(name, str):
        name = ""

    return (
        category_priority.get(
            recipe.get("recommendation_category"), 2
        ),
        _missing_weight(recipe),
        -match_score,
        name.lower(),
    )