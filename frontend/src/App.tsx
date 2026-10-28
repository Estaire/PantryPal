
import { useEffect, useRef, useState, useCallback } from "react";
import RecipeCard, { type Recipe } from "./components/RecipeCard";
import RecipeDetailPanel from "./components/RecipeDetailPanel";
import UserMenu from "./components/auth/UserMenu";
import { useAuth } from "./context/AuthContext";
import { usePersistentPantry } from "./hooks/usePersistentPantry";
import { useRecipeSearch } from "./hooks/useRecipeSearch";
import {
  API_BASE,
  useSavedRecipes,
  type SavedRecipe,
} from "./hooks/useSavedRecipes";
import SavedRecipesView from "./components/SavedRecipesView";

const BACK_TO_TOP_OFFSET = 900;

const SECTION_DEFINITIONS = [
  {
    key: "ready_to_cook",
    title: "Ready to cook",
    description: "Recipes you can make with what you have.",
  },
  {
    key: "almost_there",
    title: "Almost there",
    description: "Recipes that need just a few more ingredients.",
  },
  {
    key: "more_ingredients_needed",
    title: "More ingredients needed",
    description: "Ideas to save for your next grocery trip.",
  },
];

function App() {
  const [ingredientInput, setIngredientInput] = useState("");
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [view, setView] = useState<"search" | "saved">("search");
  const [openError, setOpenError] = useState("");

  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const { user, token, authLoading } = useAuth();
  const saved = useSavedRecipes(token);

  const {
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
  } = useRecipeSearch({
    ingredients,
    setIngredients,
    ingredientInput,
    setIngredientInput,
    selectedRecipe,
    setSelectedRecipe,
  });

  const clearAccountData = useCallback(() => {
    invalidateSearch();
    clearResults();
    setSelectedRecipe(null);
    setError("");
  }, [invalidateSearch, clearResults, setError]);

  const { syncError } = usePersistentPantry({
    user,
    token,
    authLoading,
    ingredients,
    setIngredients,
    onSignedOut: clearAccountData,
  });

  // Back-to-top button visibility.
  useEffect(() => {
    function handleScroll() {
      setShowBackToTop(window.scrollY > BACK_TO_TOP_OFFSET);
    }

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Infinite scroll: load the next page when the sentinel nears the viewport.
  // Stop automatic loading after an error so the user can retry manually.
  useEffect(() => {
    const node = sentinelRef.current;

    if (!node || !hasMore || loading || loadingMore || loadMoreError) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          void loadMore();
        }
      },
      { rootMargin: "600px 0px" },
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [
    hasMore,
    loading,
    loadingMore,
    loadMoreError,
    recipes.length,
    loadMore,
  ]);

  const sections = SECTION_DEFINITIONS.map((section) => ({
    ...section,
    items: recipes.filter(
      (recipe) => recipe.recommendation_category === section.key,
    ),
  }));

  async function openSavedRecipe(saved: SavedRecipe) {
    setOpenError("");

    const params = new URLSearchParams();
    ingredients.forEach((item) => params.append("ingredients", item));

    try {
      const res = await fetch(
        `${API_BASE}/api/v1/recipes/${encodeURIComponent(saved.id)}?${params.toString()}`,
      );
      if (!res.ok) throw new Error(`Request failed with ${res.status}`);

      setSelectedRecipe((await res.json()) as Recipe);
    } catch {
      setOpenError("This recipe couldn't be loaded right now. Please try again.");
    }
  }

  return (
    <main className="min-h-screen bg-stone-50 text-stone-900">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-3 sm:px-6 sm:py-5">
          <a href="/" className="text-2xl font-bold tracking-tight">
            PantryPal<span className="text-emerald-600">.</span>
          </a>

          <div className="flex items-center gap-1 sm:gap-4">
            {user && (
              <button
                type="button"
                onClick={() => setView(view === "saved" ? "search" : "saved")}
                className="inline-flex items-center gap-2 rounded-full px-2 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100 sm:px-3"
              >
                {view === "saved" ? (
                  "Find recipes"
                ) : (
                  <>
                    <span className="hidden sm:inline">My Cookbook</span>
                    <span className="sm:hidden">Cookbook</span>
                    <span
                      aria-hidden="true"
                      className="flex h-6 min-w-6 items-center justify-center rounded-full bg-emerald-700 px-1.5 text-xs font-bold text-white"
                    >
                      {saved.savedRecipes.length}
                    </span>
                    <span className="sr-only">
                      {saved.savedRecipes.length} saved recipes
                    </span>
                  </>
                )}
              </button>
            )}
            <UserMenu />
          </div>
        </div>
      </header>
      
      {view === "search" && (
      <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-16">
        <div className="max-w-3xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
            Your kitchen, reimagined
          </p>

          <h1 className="text-4xl font-bold leading-tight tracking-tight sm:text-6xl">
            Good food starts with
            <span className="text-emerald-700"> what you have.</span>
          </h1>

          <p className="mt-5 max-w-2xl text-lg leading-8 text-stone-600">
            Tell us what is in your pantry. We’ll find recipes you
            can make and suggest alternatives for missing ingredients.
          </p>

          <div className="mt-8 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-6">
            <label
              htmlFor="ingredient-input"
              className="mb-3 block font-semibold"
            >
              What ingredients do you have?
            </label>

            <input
              id="ingredient-input"
              type="text"
              value={ingredientInput}
              onChange={(event) => setIngredientInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void findRecipes();
                }
              }}
              disabled={loading}
              placeholder="e.g. chicken, rice, coconut milk"
              className="w-full min-w-0 rounded-xl border border-stone-300 px-4 py-3 text-base outline-none transition focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 disabled:bg-stone-100"
            />

            <div className="mt-4 flex min-h-12 flex-wrap content-start gap-2">
              {ingredients.map((ingredient) => (
                <span
                  key={ingredient}
                  className="inline-flex items-center gap-2 rounded-full bg-emerald-50 py-2 pl-3 pr-2 text-sm font-medium text-emerald-900"
                >
                  {ingredient}

                  <button
                    type="button"
                    onClick={() => removeIngredient(ingredient)}
                    aria-label={`Remove ${ingredient}`}
                    className="flex h-7 w-7 items-center justify-center rounded-full text-emerald-800 hover:bg-emerald-200 sm:h-5 sm:w-5"
                  >
                    ×
                  </button>
                </span>
              ))}

              {ingredients.length === 0 && (
                <p className="py-2 text-sm text-stone-400">
                  Your ingredients will appear here.
                </p>
              )}
            </div>

            {syncError && user && (
              <p
                role="alert"
                className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-800"
              >
                Pantry sync issue: {syncError}
              </p>
            )}

            <button
              type="button"
              onClick={() => void findRecipes()}
              disabled={loading}
              className="mt-5 w-full rounded-full bg-emerald-700 px-6 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              {loading ? "Finding recipes..." : "Find recipes"}
            </button>
          </div>
        </div>

        {error && (
          <p
            role="alert"
            className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700"
          >
            {error}
          </p>
        )}

        {loading && (
          <p className="mt-8 text-stone-600" aria-live="polite">
            Searching for recipes...
          </p>
        )}

        {recipes.length > 0 && (
          <section id="recipe-results" className="mt-14">
            <div className="mb-6">
              <h2 className="text-2xl font-bold">
                Recipes for your pantry
              </h2>

              <p className="mt-1 text-stone-600">
                {total} recipes found, ranked by ingredient match.
                {" "}Showing {recipes.length} of {total}.
              </p>
            </div>

            {sections.map((section) =>
              section.items.length > 0 ? (
                <section key={section.key} className="mt-10">
                  <div className="mb-5">
                    <h3 className="text-2xl font-bold">
                      {section.title}
                      <span className="ml-2 text-sm font-medium text-stone-400">
                        {counts[section.key] ?? section.items.length}
                      </span>
                    </h3>

                    <p className="mt-1 text-stone-600">
                      {section.description}
                    </p>
                  </div>

                  <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {section.items.map((recipe) => (
                      <RecipeCard
                        key={recipe.id}
                        recipe={recipe}
                        onViewDetails={setSelectedRecipe}
                      />
                    ))}
                  </div>
                </section>
              ) : null,
            )}

            {hasMore ? (
              <div
                ref={sentinelRef}
                className="mt-12 flex flex-col items-center gap-3 py-6"
              >
                {loadMoreError && (
                  <p role="alert" className="text-sm text-red-700">
                    {loadMoreError}
                  </p>
                )}

                <button
                  type="button"
                  onClick={() => {
                    if (loadMoreError) {
                      retryLoadMore();
                    } else {
                      void loadMore();
                    }
                  }}
                  disabled={loadingMore || loading}
                  className="rounded-lg border border-stone-300 bg-white px-5 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loadingMore
                    ? "Loading more recipes..."
                    : loadMoreError
                      ? "Try again"
                      : "Show more recipes"}
                </button>
              </div>
            ) : (
              <p className="mt-12 text-center text-sm text-stone-500">
                You’ve seen all {total} recipes.
              </p>
            )}
          </section>
        )}
      </section>
      )}

      {view === "saved" && (
        <SavedRecipesView
          signedIn={Boolean(user)}
          authLoading={authLoading}
          recipes={saved.savedRecipes}
          loading={saved.savedLoading}
          error={openError || saved.saveError}
          isPending={saved.isPending}
          onOpen={(recipe) => void openSavedRecipe(recipe)}
          onRemove={(recipe) => void saved.toggleSaved(recipe)}
          onBack={() => setView("search")}
        />
      )}

      {showBackToTop && !selectedRecipe && (
        <button
          type="button"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          aria-label="Back to top"
          className="fixed bottom-6 right-6 z-30 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-700 text-xl text-white shadow-lg transition hover:bg-emerald-800"
        >
          ↑
        </button>
      )}

      {selectedRecipe && (
        <RecipeDetailPanel
          recipe={selectedRecipe}
          onClose={() => setSelectedRecipe(null)}
          pantryIngredients={ingredients}
          onTogglePantryIngredient={togglePantryIngredient}
          isSaved={saved.isSaved(selectedRecipe.id)}
          isSavePending={saved.isPending(selectedRecipe.id)}
          onToggleSave={
            user ? () => void saved.toggleSaved(selectedRecipe) : null
          }
          saveError={saved.saveError}
        />
      )}
    </main>
  );
}

export default App;
