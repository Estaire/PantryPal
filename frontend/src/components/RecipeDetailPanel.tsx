
import type { Recipe } from "./RecipeCard";

type RecipeDetailPanelProps = {
  recipe: Recipe;
  onClose: () => void;
  pantryIngredients: string[];
  onTogglePantryIngredient: (
    ingredient: string,
    shouldBeInPantry: boolean,
  ) => void | Promise<void>;
  isSaved: boolean;
  isSavePending: boolean;
  onToggleSave: (() => void) | null;
  saveError: string;
};

function qualityStyles(quality: "great" | "good" | "fair") {
  switch (quality) {
    case "great":
      return "bg-emerald-100 text-emerald-800";
    case "good":
      return "bg-sky-100 text-sky-800";
    case "fair":
      return "bg-amber-100 text-amber-800";
  }
}

export default function RecipeDetailPanel({
  recipe,
  onClose,
  pantryIngredients,
  onTogglePantryIngredient,
  isSaved,
  isSavePending,
  onToggleSave,
  saveError,
}: RecipeDetailPanelProps) {
  const missingIngredients = recipe.missing_ingredients ?? [];
  const availableSubstitutions = recipe.available_substitutions ?? {};
  const possibleSubstitutions = recipe.substitutions ?? {};
  const substitutionDetails = recipe.substitution_details ?? {};

  // Pantry entries and ingredient.canonical are both backend canonical names.
  const pantrySet = new Set(pantryIngredients);
  const missingSet = new Set(missingIngredients);

  const checkedCount = recipe.ingredients.filter((ingredient) =>
    pantrySet.has(ingredient.canonical),
  ).length;


  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/70 p-0 backdrop-blur-sm sm:p-5 lg:p-8"
      onClick={onClose}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="recipe-detail-title"
        className="relative flex h-[100dvh] max-h-[100dvh] w-full max-w-6xl flex-col overflow-hidden bg-white shadow-2xl sm:h-auto sm:max-h-[92vh] sm:rounded-3xl"
        onClick={(event) => event.stopPropagation()}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close recipe details"
          className="absolute right-4 top-4 z-20 flex h-11 w-11 items-center justify-center rounded-full bg-white/95 text-3xl text-stone-800 shadow-lg transition hover:bg-stone-100"
        >
          ×
        </button>

        <div className="min-h-0 flex-1 overflow-y-auto">
          {/* Recipe hero */}
          <div className="relative">
            {recipe.image ? (
              <img
                src={recipe.image}
                alt={recipe.name || "Recipe"}
                className="h-90 w-full object-cover sm:h-90 lg:h-110"
              />
            ) : (
              <div className="flex h-56 items-center justify-center bg-stone-100 text-stone-500 sm:h-72 lg:h-80">
                No image available
              </div>
            )}

            <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />

            <div className="absolute inset-x-0 bottom-0 p-5 text-white sm:p-8 lg:p-10">
              <div className="mb-3 flex flex-wrap gap-2">
                <span className="rounded-full bg-emerald-500 px-3 py-2 font-semibold text-white">
                  {Number.isFinite(recipe.match_score)
                    ? `${recipe.match_score}% match`
                    : "Match unavailable"}
                </span>

                <span className="rounded-full bg-black/40 px-3 py-2 font-medium backdrop-blur-md">
                  {missingIngredients.length === 0
                    ? "Ready to cook"
                    : `${missingIngredients.length} missing`}
                </span>
                {onToggleSave ? (
                  <button
                    type="button"
                    onClick={onToggleSave}
                    disabled={isSavePending}
                    aria-pressed={isSaved}
                    className={`rounded-full px-3 py-2 font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 sm:py-1.5 ${
                      isSaved
                        ? "bg-white text-emerald-800 hover:bg-emerald-50"
                        : "bg-black/40 text-white backdrop-blur-md hover:bg-black/20"
                    }`}
                  >
                    {isSavePending ? "Saving..." : isSaved ? "✓ Saved" : "Save recipe"}
                  </button>
                ) : (
                  <span className="rounded-full bg-black/40 px-3 py-2 font-medium backdrop-blur-md">
                    Sign in to save
                  </span>
                )}
              </div>

              <h2
                id="recipe-detail-title"
                className="max-w-4xl text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl"
              >
                {recipe.name || "Untitled recipe"}
              </h2>
            </div>
          </div>
          {/*
          <div className="grid grid-cols-3 gap-3 border-b border-stone-200 px-5 py-5 sm:px-8 lg:px-10">
            {[
              { label: "Servings", value: recipe.servings },
              { label: "Prep time", value: recipe.prep_time },
              { label: "Cook time", value: recipe.cook_time },
            ]
              .filter((item) => item.value != null && item.value !== "")
              .map((item) => (
                <div key={item.label} className="rounded-xl bg-stone-50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-stone-500">
                    {item.label}
                  </p>
                  <p className="mt-1 text-lg font-bold text-stone-900">
                    {item.value}
                    {item.label !== "Servings" &&
                    typeof item.value === "number"
                      ? " min"
                      : ""}
                  </p>
                </div>
              ))}
          </div>
          */}

          {/* Recipe content */}
          <div className="p-5 sm:p-8 lg:p-10">
            <div className="mb-8 border-b border-stone-200 pb-6">
              <p className="text-sm leading-6 text-stone-500">
                Check off ingredients as you prepare them. Your pantry match
                and suggested alternatives help you decide what to use.
              </p>
              {saveError && (
                <p role="alert" className="mb-6 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  {saveError}
                </p>
              )}
            </div>

            <div className="grid gap-10 lg:grid-cols-[minmax(280px,0.85fr)_minmax(0,1.5fr)] lg:gap-14">
              {/* Ingredients column */}
              <aside>
                <div className="mb-5 flex items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
                      Get prepared
                    </p>
                    <h3 className="mt-1 text-2xl font-bold text-stone-900">
                      Ingredients
                    </h3>
                  </div>

                  <span className="text-sm text-stone-500">
                    {checkedCount}/{recipe.ingredients.length}
                  </span>
                </div>

                <div className="mb-5 h-1.5 overflow-hidden rounded-full bg-stone-100">
                  <div
                    className="h-full rounded-full bg-emerald-600 transition-all"
                    style={{
                      width: `${
                        recipe.ingredients.length > 0
                          ? (checkedCount / recipe.ingredients.length) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>

                <ul className="space-y-1">
                  {recipe.ingredients.map((ingredient, index) => {
                    const ingredientName = ingredient.name;
                    const ingredientMeasure = ingredient.measure?.trim() ?? "";
                    const checked = pantrySet.has(ingredient.canonical);
                    const missing = missingSet.has(ingredient.canonical);

                    return (
                      <li key={`${ingredientName}-${index}`}>
                        <label className="flex cursor-pointer items-start gap-3 rounded-xl p-3 transition hover:bg-stone-50">
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={(event) =>
                              void onTogglePantryIngredient(
                                ingredient.canonical,
                                event.target.checked,
                              )
                            }
                            className="mt-1 h-4 w-4 shrink-0 accent-emerald-700"
                          />

                          <span className="text-sm leading-6 text-stone-700">
                            {ingredientMeasure && (
                              <span className="mr-1 font-semibold text-stone-900">
                                {ingredientMeasure}
                              </span>
                            )}

                            {ingredientName}

                            {missing && !checked && (
                              <span className="ml-2 inline-block rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                                Missing
                              </span>
                            )}
                          </span>
                        </label>
                      </li>
                    );
                  })}
                </ul>
              </aside>

              {/* Instructions column */}
              <section>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
                  Let's get cooking
                </p>

                <h3 className="mt-1 text-2xl font-bold text-stone-900">
                  Instructions
                </h3>

                <div className="mt-6">
                  {recipe.instructions ? (
                    <ol className="space-y-5">
                      {recipe.instructions
                        .replace(/\r\n/g, "\n")
                        // Remove leading step numbers or "Step X" markers at the start of lines
                        .replace(/^(?:step\s*)?\d+[.)]\s*/gim, "")
                        .split(/\n+/)
                        .map((step) => step.trim())
                        // Filter out empty strings AND any lines that are just numbers/step labels
                        .filter((step) => step.length > 0 && !/^(?:step\s*)?\d+[.)]?$/i.test(step))
                        .map((step, index) => (
                          <li
                            key={`${index}-${step}`}
                            className="flex items-start gap-4"
                          >
                            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-sm font-bold text-emerald-800">
                              {index + 1}
                            </span>

                            <p className="flex-1 pt-1 leading-7 text-stone-700">
                              {step}
                            </p>
                          </li>
                        ))}
                    </ol>
                  ) : (
                    <p className="text-stone-500">
                      No instructions are available for this recipe.
                    </p>
                  )}
                </div>
              </section>
            </div>
            
            {/* Substitution explorer */}
            {(Object.keys(availableSubstitutions).length > 0 ||
              Object.keys(possibleSubstitutions).length > 0) && (
              <section className="mt-12 border-t border-stone-200 pt-8">
                <div className="mb-6">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
                    Cook with confidence
                  </p>
                  <h3 className="mt-1 text-2xl font-bold text-stone-900">
                    Ingredient alternatives
                  </h3>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-stone-500">
                    See what you can replace with ingredients you already own,
                    plus other alternatives and tips for using them successfully.
                  </p>
                </div>

                <div className="grid items-start gap-6 md:grid-cols-2">
                  {/* Pantry-available substitutions */}
                  <section className="min-w-0 rounded-2xl border border-emerald-200 bg-emerald-50/50 p-5 sm:p-6">
                    <div className="mb-5 flex items-start gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800">
                        ✓
                      </div>
                      <div>
                        <h4 className="font-bold text-stone-900">
                          Available substitutions
                        </h4>
                        <p className="mt-1 text-sm leading-5 text-stone-600">
                          Reliable alternatives already in your pantry.
                        </p>
                      </div>
                    </div>

                    {Object.keys(availableSubstitutions).length > 0 ? (
                      <div className="space-y-4">
                        {Object.entries(availableSubstitutions).map(
                          ([ingredient, alternatives]) => {
                            const details = substitutionDetails[ingredient] ?? [];
                            return (
                              <div
                                key={ingredient}
                                className="rounded-xl border border-emerald-100 bg-white p-4"
                              >
                                <p className="text-sm font-semibold text-stone-900">
                                  Replace {ingredient} with:
                                </p>

                                <div className="mt-3 space-y-3">
                                  {alternatives.map((alternative) => {
                                    const detail = details.find((item) => item.ingredient === alternative);

                                    return (
                                      <div
                                        key={alternative}
                                        className="border-l-2 border-emerald-300 pl-3"
                                      >
                                        <div className="flex flex-wrap items-center gap-2">
                                          <span className="font-medium text-stone-800">
                                            {alternative}
                                          </span>

                                          {detail && (
                                            <span
                                              className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${qualityStyles(detail.quality)}`}
                                            >
                                              {detail.quality} match
                                            </span>
                                          )}
                                        </div>

                                        {detail?.note && (
                                          <p className="mt-1.5 text-sm leading-6 text-stone-600">
                                            {detail.note}
                                          </p>
                                        )}

                                        {detail && (
                                          <p className="mt-2 text-xs font-medium text-emerald-800">
                                            {detail.quality === "great"
                                              ? "Excellent replacement"
                                              : "Reliable replacement"}
                                            {detail.credit > 0
                                              ? ` · ${Math.round(detail.credit * 100)}% match credit`
                                              : ""}
                                          </p>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            );
                          },
                        )}
                      </div>
                    ) : (
                      <p className="rounded-xl bg-white p-4 text-sm leading-6 text-stone-600">
                        None of the suggested replacements are currently available
                        in your pantry.
                      </p>
                    )}
                  </section>

                  {/* Other suggested alternatives */}
                  <section className="min-w-0 rounded-2xl border border-stone-200 bg-stone-50/70 p-5 sm:p-6">
                    <div className="mb-5 flex items-start gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800">
                        <span aria-hidden="true">✳</span>
                      </div>
                      <div>
                        <h4 className="font-bold text-stone-900">
                          Other alternatives
                        </h4>
                        <p className="mt-1 text-sm leading-5 text-stone-600">
                          More options to consider, including context-dependent swaps.
                        </p>
                      </div>
                    </div>

                    {Object.keys(possibleSubstitutions).length > 0 ? (
                      <div className="space-y-4">
                        {Object.entries(possibleSubstitutions).map(
                          ([ingredient, alternatives]) => {
                            const details = substitutionDetails[ingredient] ?? [];

                            return (
                              <div
                                key={ingredient}
                                className="rounded-xl border border-stone-200 bg-white p-4"
                              >
                                <p className="text-sm font-semibold text-stone-900">
                                  Instead of {ingredient}
                                </p>

                                <div className="mt-3 space-y-3">
                                  {alternatives.map((alternative) => {
                                    const detail = details.find((item) => item.ingredient === alternative);

                                    const inPantry = pantrySet.has(alternative);

                                    return (
                                      <div
                                        key={alternative}
                                        className="border-l-2 border-stone-200 pl-3"
                                      >
                                        <div className="flex flex-wrap items-center gap-2">
                                          <span className="font-medium text-stone-800">
                                            {alternative}
                                          </span>

                                          {detail && (
                                            <span
                                              className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${qualityStyles(detail.quality)}`}
                                            >
                                              {detail.quality}
                                            </span>
                                          )}

                                          {inPantry && (
                                            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">
                                              In pantry
                                            </span>
                                          )}
                                        </div>

                                        {detail?.note && (
                                          <p className="mt-1.5 text-sm leading-6 text-stone-600">
                                            {detail.note}
                                          </p>
                                        )}

                                        {detail?.quality === "fair" && (
                                          <p className="mt-2 text-xs leading-5 text-amber-800">
                                            Best for certain recipes; the result may
                                            differ in flavour, texture, or method.
                                          </p>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            );
                          },
                        )}
                      </div>
                    ) : (
                      <p className="rounded-xl bg-white p-4 text-sm leading-6 text-stone-600">
                        No additional alternatives are available for this recipe.
                      </p>
                    )}
                  </section>
                </div>
              </section>
            )}

            <div className="mt-12 border-t border-stone-200 pt-6">
              <button
                type="button"
                onClick={onClose}
                className="rounded-full bg-stone-900 px-6 py-3 font-semibold text-white transition hover:bg-stone-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2"
              >
                Back to recipes
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
