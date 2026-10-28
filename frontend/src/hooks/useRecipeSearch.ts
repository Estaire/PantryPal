import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";

import type { Recipe } from "../components/RecipeCard";
import {
  createRequest,
  fetchRecipe,
  fetchRecipePage,
  MAX_PAGE_LIMIT,
  PAGE_SIZE,
  type RecipePage,
} from "../services/recipes";
import {
  combineIngredients,
} from "../utils/ingredients";

const REFRESH_DEBOUNCE_MS = 700;

interface UseRecipeSearchOptions {
  ingredients: string[];
  setIngredients: Dispatch<SetStateAction<string[]>>;
  ingredientInput: string;
  setIngredientInput: Dispatch<SetStateAction<string>>;
  selectedRecipe: Recipe | null;
  setSelectedRecipe: Dispatch<SetStateAction<Recipe | null>>;
}

export function useRecipeSearch({
  ingredients,
  setIngredients,
  ingredientInput,
  setIngredientInput,
  selectedRecipe,
  setSelectedRecipe,
}: UseRecipeSearchOptions) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState("");
  const [error, setError] = useState("");

  const requestIdRef = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);
  const loadMoreControllerRef = useRef<AbortController | null>(null);
  const loadingMoreRef = useRef(false);
  const refreshTimerRef = useRef<number | null>(null);

  const activeIngredientsRef = useRef<string[]>([]);
  const recipesRef = useRef<Recipe[]>([]);
  const loadMoreRef = useRef<() => Promise<void>>(async () => {});

  const cancelPendingRefresh = useCallback(() => {
    if (refreshTimerRef.current !== null) {
      window.clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  const abortLoadMore = useCallback(() => {
    loadMoreControllerRef.current?.abort();
    loadMoreControllerRef.current = null;
    loadingMoreRef.current = false;
    setLoadingMore(false);
    setLoadMoreError("");
  }, []);

  const invalidateSearch = useCallback(() => {
    cancelPendingRefresh();
    requestIdRef.current += 1;
    controllerRef.current?.abort();
    controllerRef.current = null;
    abortLoadMore();
    setLoading(false);
  }, [abortLoadMore, cancelPendingRefresh]);

  const clearResults = useCallback(() => {
    setRecipes([]);
    setTotal(0);
    setHasMore(false);
    setCounts({});
    activeIngredientsRef.current = [];
    recipesRef.current = [];
  }, []);

  const applyPage = useCallback((page: RecipePage) => {
    setRecipes(page.recipes);
    recipesRef.current = page.recipes;
    setTotal(page.total);
    setHasMore(page.has_more);
    setCounts(page.counts ?? {});
  }, []);

  useEffect(() => {
    recipesRef.current = recipes;
  }, [recipes]);

  useEffect(() => {
    return () => {
      cancelPendingRefresh();
      requestIdRef.current += 1;
      controllerRef.current?.abort();
      loadMoreControllerRef.current?.abort();
    };
  }, [cancelPendingRefresh]);

  const removeIngredient = useCallback(
    (ingredientToRemove: string) => {
      invalidateSearch();

      setIngredients((current) =>
        current.filter((item) => item !== ingredientToRemove),
      );

      clearResults();
      setError("");
    },
    [clearResults, invalidateSearch, setIngredients],
  );

  const findRecipes = useCallback(async () => {
    const searchIngredients = combineIngredients(
      ingredients,
      ingredientInput,
    );

    if (searchIngredients.length === 0) {
      setError("Enter at least one ingredient to find recipes.");
      return;
    }

    cancelPendingRefresh();
    abortLoadMore();

    controllerRef.current?.abort();

    const request = createRequest();
    controllerRef.current = request.controller;
    const requestId = ++requestIdRef.current;

    setLoading(true);
    setError("");
    clearResults();

    try {
      const page = await fetchRecipePage(
        searchIngredients,
        0,
        PAGE_SIZE,
        request.controller.signal,
      );

      if (requestId !== requestIdRef.current) return;

      // Show the server's canonical names only once the search has succeeded.
      activeIngredientsRef.current = page.pantry;
      setIngredients(page.pantry);
      setIngredientInput("");
      applyPage(page);

      if (page.total === 0) {
        setError("No recipes found. Try different ingredients.");
      }
    } catch (err) {
      if (requestId !== requestIdRef.current) return;

      if (err instanceof Error && err.name === "AbortError") {
        if (request.didTimeOut()) {
          setError(
            "The recipe search timed out. Check that the backend is running and try again.",
          );
        }
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while retrieving recipes.",
      );
    } finally {
      request.done();

      if (requestId === requestIdRef.current) {
        setLoading(false);
        controllerRef.current = null;
      }
    }
  }, [
    ingredients,
    ingredientInput,
    setIngredients,
    setIngredientInput,
    cancelPendingRefresh,
    abortLoadMore,
    clearResults,
    applyPage,
  ]);

  const loadMore = useCallback(async () => {
    if (loadingMoreRef.current || loading || !hasMore) return;

    const searchIngredients = activeIngredientsRef.current;
    if (searchIngredients.length === 0) return;

    const requestId = requestIdRef.current;
    const offset = recipesRef.current.length;
    const request = createRequest();

    loadMoreControllerRef.current = request.controller;
    loadingMoreRef.current = true;
    setLoadingMore(true);
    setLoadMoreError("");

    try {
      const page = await fetchRecipePage(
        searchIngredients,
        offset,
        PAGE_SIZE,
        request.controller.signal,
      );

      if (requestId !== requestIdRef.current) return;

      const seen = new Set(recipesRef.current.map((recipe) => recipe.id));
      const fresh = page.recipes.filter((recipe) => !seen.has(recipe.id));

      setTotal(page.total);
      setCounts(page.counts ?? {});

      if (fresh.length === 0) {
        setHasMore(false);
      } else {
        setRecipes((current) => {
          const updated = [...current, ...fresh];
          recipesRef.current = updated;
          return updated;
        });
        setHasMore(page.has_more);
      }
    } catch (err) {
      if (requestId !== requestIdRef.current) return;

      if (err instanceof Error && err.name === "AbortError") {
        if (request.didTimeOut()) {
          setLoadMoreError("Loading more recipes timed out.");
        }
        return;
      }

      setLoadMoreError(
        err instanceof Error
          ? err.message
          : "Could not load more recipes.",
      );
    } finally {
      request.done();

      if (requestId === requestIdRef.current) {
        loadingMoreRef.current = false;
        setLoadingMore(false);
        loadMoreControllerRef.current = null;
      }
    }
  }, [loading, hasMore]);

  useEffect(() => {
    loadMoreRef.current = loadMore;
  }, [loadMore]);

  const refreshRecommendations = useCallback(
    async (searchIngredients: string[], selectedRecipeId: string) => {
      abortLoadMore();
      controllerRef.current?.abort();

      const request = createRequest();
      controllerRef.current = request.controller;
      const requestId = ++requestIdRef.current;

      const limit = Math.min(
        Math.max(recipesRef.current.length, PAGE_SIZE),
        MAX_PAGE_LIMIT,
      );

      setLoading(true);
      setError("");

      try {
        const [page, updatedRecipe] = await Promise.all([
          fetchRecipePage(
            searchIngredients,
            0,
            limit,
            request.controller.signal,
          ),
          fetchRecipe(
            selectedRecipeId,
            searchIngredients,
            request.controller.signal,
          ),
        ]);

        if (requestId !== requestIdRef.current) return;

        activeIngredientsRef.current = searchIngredients;
        applyPage(page);

        if (updatedRecipe) {
          setSelectedRecipe((current) =>
            current && current.id === updatedRecipe.id
              ? updatedRecipe
              : current,
          );
        }

        if (page.total === 0) {
          setError("No recipes found with your updated pantry.");
        }
      } catch (err) {
        if (requestId !== requestIdRef.current) return;

        if (err instanceof Error && err.name === "AbortError") {
          if (request.didTimeOut()) {
            setError("Refreshing recipes timed out. Please try again.");
          }
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong while refreshing recipes.",
        );
      } finally {
        request.done();

        if (requestId === requestIdRef.current) {
          setLoading(false);
          controllerRef.current = null;
        }
      }
    },
    [abortLoadMore, applyPage, setSelectedRecipe],
  );

  const togglePantryIngredient = useCallback(
    (ingredient: string, shouldBeInPantry: boolean) => {
      const canonical = ingredient.trim();
      if (!canonical) return;

      const updatedIngredients = shouldBeInPantry
        ? ingredients.includes(canonical)
          ? ingredients
          : [...ingredients, canonical]
        : ingredients.filter((item) => item !== canonical);

      setIngredients(updatedIngredients);

      if (selectedRecipe) {
        const recipeId = selectedRecipe.id;
        cancelPendingRefresh();

        refreshTimerRef.current = window.setTimeout(() => {
          refreshTimerRef.current = null;
          void refreshRecommendations(updatedIngredients, recipeId);
        }, REFRESH_DEBOUNCE_MS);
      }
    },
    [
      ingredients,
      selectedRecipe,
      setIngredients,
      cancelPendingRefresh,
      refreshRecommendations,
    ],
  );

  const retryLoadMore = useCallback(() => {
    setLoadMoreError("");
    void loadMoreRef.current();
  }, []);

  return {
    recipes,
    total,
    hasMore,
    counts,
    loading,
    loadingMore,
    loadMoreError,
    error,
    setError,
    findRecipes,
    loadMore,
    retryLoadMore,
    removeIngredient,
    togglePantryIngredient,
    clearResults,
    invalidateSearch,
  };
}
