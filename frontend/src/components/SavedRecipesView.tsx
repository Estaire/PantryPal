import type { SavedRecipe } from "../hooks/useSavedRecipes";

type SavedRecipesViewProps = {
  signedIn: boolean;
  authLoading: boolean;
  recipes: SavedRecipe[];
  loading: boolean;
  error: string;
  isPending: (id: string) => boolean;
  onOpen: (recipe: SavedRecipe) => void;
  onRemove: (recipe: SavedRecipe) => void;
  onBack: () => void;
};

export default function SavedRecipesView({
  signedIn,
  authLoading,
  recipes,
  loading,
  error,
  isPending,
  onOpen,
  onRemove,
  onBack,
}: SavedRecipesViewProps) {
  let content: React.ReactNode;

  if (authLoading) {
    content = <p className="text-stone-600">Checking account...</p>;
  } else if (!signedIn) {
    content = (
      <div className="rounded-2xl border border-stone-200 bg-white p-8 text-center">
        <p className="text-lg font-semibold">
          Sign in to see your saved recipes.
        </p>
        <p className="mt-2 text-stone-600">
          Use the sign-in button at the top of the page.
        </p>
      </div>
    );
  } else if (loading) {
    content = (
      <p className="text-stone-600" aria-live="polite">
        Loading saved recipes...
      </p>
    );
  } else if (recipes.length === 0) {
    content = (
      <div className="rounded-2xl border border-stone-200 bg-white p-8 text-center">
        <p className="text-lg font-semibold">No saved recipes yet.</p>
        <p className="mt-2 text-stone-600">
          Open a recipe and tap “Save recipe” to keep it here.
        </p>
      </div>
    );
  } else {
    content = (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {recipes.map((recipe) => (
          <SavedRecipeCard
            key={recipe.id}
            recipe={recipe}
            pending={isPending(recipe.id)}
            onOpen={() => onOpen(recipe)}
            onRemove={() => onRemove(recipe)}
          />
        ))}
      </div>
    );
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-16">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm mb-2 font-semibold uppercase tracking-[0.18em] text-emerald-700">
            Your cookbook
          </p>
        </div>

        <button
          type="button"
          onClick={onBack}
          className="rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100"
        >
          Back to search
        </button>
      </div>

      {error && (
        <p
          role="alert"
          className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700"
        >
          {error}
        </p>
      )}

      {content}
    </section>
  );
}

type SavedRecipeCardProps = {
  recipe: SavedRecipe;
  pending: boolean;
  onOpen: () => void;
  onRemove: () => void;
};

function SavedRecipeCard({
  recipe,
  pending,
  onOpen,
  onRemove,
}: SavedRecipeCardProps) {
  const savedDate = new Date(recipe.saved_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
      {recipe.image ? (
        <img
          src={recipe.image}
          alt={recipe.name}
          loading="lazy"
          className="h-52 w-full object-cover"
        />
      ) : (
        <div
          className="flex h-52 items-center justify-center bg-stone-100 text-stone-500"
          role="img"
          aria-label="No recipe image available"
        >
          No image available
        </div>
      )}

      <div className="flex flex-1 flex-col p-5">
        <p className="text-xs text-stone-500">Saved {savedDate}</p>
        <h3 className="mt-1 text-xl font-bold text-stone-900">{recipe.name}</h3>

        <div className="mt-auto flex gap-2 pt-5">
          <button
            type="button"
            onClick={onOpen}
            className="flex-1 rounded-full bg-stone-900 px-4 py-3 font-semibold text-white transition hover:bg-stone-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2"
          >
            View recipe
          </button>

          <button
            type="button"
            onClick={onRemove}
            disabled={pending}
            className="rounded-full border border-stone-300 px-4 py-3 font-semibold text-stone-700 transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {pending ? "Removing..." : "Remove"}
          </button>
        </div>
      </div>
    </article>
  );
}