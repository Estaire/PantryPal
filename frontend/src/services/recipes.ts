
import type { Recipe } from "../components/RecipeCard";
import { API_BASE } from "../config";

export const PAGE_SIZE = 12;
export const MAX_PAGE_LIMIT = 100;

const REQUEST_TIMEOUT_MS = 15000;

export interface RecipePage {
  recipes: Recipe[];
  pantry: string[];
  total: number;
  has_more: boolean;
  counts?: Record<string, number>;
}

export function createRequest(timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  let timedOut = false;

  const timeoutId = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  return {
    controller,
    didTimeOut: () => timedOut,
    done: () => window.clearTimeout(timeoutId),
  };
}

async function readErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data: unknown = await response.json();

    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }
  } catch {
    // The server may return a non-JSON error response.
  }

  return fallback;
}

function isRecipePage(data: unknown): data is RecipePage {
  if (typeof data !== "object" || data === null) return false;

  const page = data as Record<string, unknown>;

  return (
    Array.isArray(page.recipes) &&
    typeof page.total === "number" &&
    typeof page.has_more === "boolean"
  );
}

function buildIngredientParams(ingredients: string[]): URLSearchParams {
  const params = new URLSearchParams();

  ingredients.forEach((ingredient) => {
    params.append("ingredients", ingredient);
  });

  return params;
}

export async function fetchRecipePage(
  ingredients: string[],
  offset: number,
  limit: number,
  signal: AbortSignal,
): Promise<RecipePage> {
  const params = buildIngredientParams(ingredients);
  params.set("offset", String(offset));
  params.set("limit", String(limit));

  const response = await fetch(
    `${API_BASE}/api/v1/recipes?${params.toString()}`,
    { signal },
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, "Could not retrieve recipes."),
    );
  }

  const data: unknown = await response.json();

  if (!isRecipePage(data)) {
    throw new Error("The server returned an unexpected recipe response.");
  }

  return data;
}

export async function fetchRecipe(
  recipeId: string,
  ingredients: string[],
  signal: AbortSignal,
): Promise<Recipe | null> {
  const params = buildIngredientParams(ingredients);

  const response = await fetch(
    `${API_BASE}/api/v1/recipes/${encodeURIComponent(recipeId)}?${params.toString()}`,
    { signal },
  );

  if (response.status === 404) return null;

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, "Could not refresh this recipe."),
    );
  }

  const data: unknown = await response.json();

  if (typeof data !== "object" || data === null) {
    throw new Error("The server returned an unexpected recipe response.");
  }

  return data as Recipe;
}
