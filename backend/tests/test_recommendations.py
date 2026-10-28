import app.services.recommendations as recommendations
from app.services.recommendations import (
    calculate_substitution_score,
    expand_with_substitutes,
    find_assumed_staples,
    find_missing_ingredients,
    get_ingredient_weight,
    get_recommendation_category,
    normalize_ingredient,
    rank_recipe,
)


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def test_normalize_maps_brand_variants_to_canonical_name():
    assert normalize_ingredient("Chicken Breast") == "chicken"


def test_normalize_singularizes_last_word():
    assert normalize_ingredient("Eggs") == "egg"
    assert normalize_ingredient("Tomatoes") == "tomato"
    assert normalize_ingredient("Cherries") == "cherry"


def test_normalize_removes_preparation_words():
    assert normalize_ingredient("finely chopped onion") == "onion"
    assert normalize_ingredient("fresh basil") == "basil"


def test_normalize_follows_alias_table():
    assert normalize_ingredient("scallion") == "spring onion"
    assert normalize_ingredient("cilantro") == "coriander"
    assert normalize_ingredient("prawns") == "shrimp"


def test_normalize_handles_accents_and_punctuation():
    assert normalize_ingredient("Jalapeño") == "jalapeno"
    assert normalize_ingredient("  Garlic,  ") == "garlic"


def test_normalize_returns_empty_string_for_non_strings():
    assert normalize_ingredient(None) == ""
    assert normalize_ingredient(42) == ""


def test_normalize_is_idempotent():
    once = normalize_ingredient("Chicken Breast")
    assert normalize_ingredient(once) == once


# --------------------------------------------------------------------------- #
# Staples and missing ingredients
# --------------------------------------------------------------------------- #

def test_staples_are_never_reported_missing():
    assert find_missing_ingredients([], ["salt", "chicken"]) == ["chicken"]


def test_exact_canonical_match_is_not_missing():
    assert find_missing_ingredients(["chicken"], ["Chicken Breast"]) == []


def test_duplicate_required_ingredients_are_reported_once():
    assert find_missing_ingredients([], ["egg", "Eggs"]) == ["egg"]


def test_find_assumed_staples_returns_original_names():
    assert find_assumed_staples(["Salt", "chicken"]) == ["Salt"]


# --------------------------------------------------------------------------- #
# Weights and scoring
# --------------------------------------------------------------------------- #

def test_main_ingredients_weigh_double():
    assert get_ingredient_weight("Chicken Breast") == 2
    assert get_ingredient_weight("parsley") == 1


def test_full_pantry_match_scores_100():
    score = calculate_substitution_score(
        ["chicken", "rice"],
        ["chicken", "rice", "salt"],
    )
    assert score == 100.0


def test_score_is_weighted_by_ingredient_importance():
    # chicken (weight 2) is missing, parsley (weight 1) is present: 1 / 3.
    score = calculate_substitution_score(["parsley"], ["chicken", "parsley"])
    assert score == 33.3


def test_recipe_with_only_staples_scores_zero():
    assert calculate_substitution_score([], ["salt"]) == 0.0


# --------------------------------------------------------------------------- #
# Categories
# --------------------------------------------------------------------------- #

def test_no_missing_ingredients_is_ready_to_cook():
    category = get_recommendation_category(
        ["chicken"], [], required=["chicken"]
    )
    assert category == "ready_to_cook"


def test_small_recipe_allows_one_minor_missing_ingredient():
    required = ["parsley", "basil", "thyme"]
    category = get_recommendation_category(
        [], ["basil"], required=required
    )
    assert category == "almost_there"


def test_small_recipe_rejects_two_minor_missing_ingredients():
    required = ["parsley", "basil", "thyme"]
    category = get_recommendation_category(
        [], ["basil", "thyme"], required=required
    )
    assert category == "more_ingredients_needed"


def test_missing_main_ingredient_counts_double():
    # One missing chicken has weight 2, above the limit of 1 for a 3-item recipe.
    required = ["chicken", "parsley", "basil"]
    category = get_recommendation_category(
        [], ["chicken"], required=required
    )
    assert category == "more_ingredients_needed"


def test_without_required_uses_legacy_threshold():
    assert get_recommendation_category([], ["a", "b"]) == "almost_there"
    assert get_recommendation_category([], ["a", "b", "c"]) == "more_ingredients_needed"


# --------------------------------------------------------------------------- #
# Ranking
# --------------------------------------------------------------------------- #

def test_rank_orders_by_category_then_missing_weight_then_score():
    recipes = [
        {
            "name": "C",
            "recommendation_category": "more_ingredients_needed",
            "missing_ingredients": ["chicken"],
            "match_score": 50,
        },
        {
            "name": "B",
            "recommendation_category": "almost_there",
            "missing_ingredients": ["basil"],
            "match_score": 80,
        },
        {
            "name": "A",
            "recommendation_category": "ready_to_cook",
            "missing_ingredients": [],
            "match_score": 100,
        },
    ]

    ordered = [recipe["name"] for recipe in sorted(recipes, key=rank_recipe)]
    assert ordered == ["A", "B", "C"]


def test_rank_puts_lighter_missing_first_within_category():
    light = {
        "name": "Light",
        "recommendation_category": "almost_there",
        "missing_ingredients": ["parsley"],
        "match_score": 60,
    }
    heavy = {
        "name": "Heavy",
        "recommendation_category": "almost_there",
        "missing_ingredients": ["chicken"],
        "match_score": 90,
    }

    ordered = sorted([heavy, light], key=rank_recipe)
    assert [recipe["name"] for recipe in ordered] == ["Light", "Heavy"]


# --------------------------------------------------------------------------- #
# Substitution expansion
# --------------------------------------------------------------------------- #

def test_expansion_keeps_pantry_items(monkeypatch):
    monkeypatch.setattr(recommendations, "_REVERSE_USABLE_SUBSTITUTES", {})

    assert expand_with_substitutes(["chicken"]) == ["chicken"]


def test_expansion_adds_one_level_only(monkeypatch):
    # soy milk replaces milk, and oat milk replaces soy milk. A pantry with
    # oat milk must not unlock milk through the chain.
    monkeypatch.setattr(
        recommendations,
        "_REVERSE_USABLE_SUBSTITUTES",
        {"soy milk": ["milk"], "oat milk": ["soy milk"]},
    )

    expanded = expand_with_substitutes(["oat milk"])

    assert "soy milk" in expanded
    assert "milk" not in expanded


def test_expansion_does_not_duplicate(monkeypatch):
    monkeypatch.setattr(
        recommendations,
        "_REVERSE_USABLE_SUBSTITUTES",
        {"soy milk": ["milk"]},
    )

    expanded = expand_with_substitutes(["soy milk", "milk"])

    assert expanded.count("milk") == 1
    

# --------------------------------------------------------------------------- #
# Expansion against the real substitution table (no monkeypatching)
# --------------------------------------------------------------------------- #

def test_expansion_uses_real_substitution_table():
    pairs = [
        (alternative, needed)
        for alternative, needed_list in recommendations._REVERSE_USABLE_SUBSTITUTES.items()
        for needed in needed_list
    ]

    assert pairs, "The substitution table is empty; the reverse lookup did not build."

    # Check a sample so the test stays fast if the table grows.
    for alternative, needed in pairs[:50]:
        assert needed in expand_with_substitutes([alternative]), (
            f"Pantry with {alternative!r} should unlock {needed!r}"
        )