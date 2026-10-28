export type SubstitutionDetail = {
  ingredient: string;
  quality: "great" | "good" | "fair";
  credit: number;
  note: string;
  counts_as_available: boolean;
};

export type RecommendationCategory =
  | "ready_to_cook"
  | "almost_there"
  | "more_ingredients_needed";

export type Recipe = {
    id: string;
    name: string;
    image: string;
    ingredients: {
        name: string;
        measure: string;
        canonical: string;
    }[];
    instructions: string;
    match_score: number;
    missing_ingredients: string[];
    status: "ready_to_cook" | "missing_ingredients";
    substitutions: Record<string, string[]>;
    missing_count: number;
    recommendation_category: RecommendationCategory;
    available_substitutions: Record<string, string[]>;
    substitution_details?: Record<string, SubstitutionDetail[]>;
};

type RecipeCardProps = {
  recipe: Recipe;
  onViewDetails: (recipe: Recipe) => void;
};

export default function RecipeCard({
  recipe,
  onViewDetails,
}: RecipeCardProps) {
  const missingIngredients = recipe.missing_ingredients ?? [];
  const availableSubstitutions = recipe.available_substitutions ?? {};
  const possibleSubstitutions = recipe.substitutions ?? {};

  const availableSwapCount = Object.values(availableSubstitutions)
    .reduce((total, alternatives) => total + alternatives.length, 0);

  const possibleSwapCount = Object.values(possibleSubstitutions)
    .reduce((total, alternatives) => total + alternatives.length, 0);

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md">
      {recipe.image ? (
        <img
          src={recipe.image}
          alt={recipe.name || "Recipe"}
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
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-800">
            {Number.isFinite(recipe.match_score)
              ? `${recipe.match_score}% match`
              : "Match unavailable"}
          </span>

          <span className="text-xs text-stone-500">
            {missingIngredients.length === 0
              ? "Ready to cook"
              : `${missingIngredients.length} missing`}
          </span>
        </div>

        <h3 className="text-xl font-bold text-stone-900">
          {recipe.name || "Untitled recipe"}
        </h3>

        {missingIngredients.length > 0 && (
            <p className="mt-3 mb-5 line-clamp-2 text-sm leading-6 text-stone-600">
                Missing: {missingIngredients.join(", ")}
            </p>
        )}

        <div className="mt-auto pt-5">
        {(availableSwapCount > 0 || possibleSwapCount > 0) && (
            <div className="mb-5 flex flex-wrap gap-2 text-xs font-medium">
            {availableSwapCount > 0 && (
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-800">
                ↔ {availableSwapCount} available swaps
                </span>
            )}

            {possibleSwapCount > 0 && (
                <span className="rounded-full bg-amber-50 px-2.5 py-1 text-amber-800">
                +{possibleSwapCount} alternatives
                </span>
            )}
            </div>
        )}
        </div>

        <button
          type="button"
          onClick={() => onViewDetails(recipe)}
        className="w-full rounded-full bg-stone-900 px-4 py-3 font-semibold text-white transition hover:bg-stone-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2"        >
          View recipe
        </button>
      </div>
    </article>
  );
}
