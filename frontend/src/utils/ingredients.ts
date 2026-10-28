/** Light cleanup for display and duplicate checks. The backend owns canonical names. */
function tidy(ingredient: string): string {
  return ingredient.trim().replace(/\s+/g, " ");
}

/**
 * Combine the existing pantry with ingredients entered by the user.
 * Accept commas, semicolons, and new lines as separators.
 * Ignore empty values and duplicates.
 */
export function combineIngredients(
  existingIngredients: string[],
  input: string,
): string[] {
  const entered = input
    .split(/[,;\n]+/)
    .map(tidy)
    .filter(Boolean);

  const combined = [...existingIngredients];
  const seen = new Set(existingIngredients.map(tidy));

  for (const ingredient of entered) {
    if (!seen.has(ingredient)) {
      combined.push(ingredient);
      seen.add(ingredient);
    }
  }

  return combined;
}