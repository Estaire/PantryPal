import { useCallback, useEffect, useMemo, useState } from "react";
import { API_BASE } from "../config";

export type SavedRecipe = {
  id: string;
  name: string;
  image: string;
  ingredients: { name: string; measure: string }[];
  instructions: string;
  saved_at: string;
};

// The fields needed to save a recipe. Recipe satisfies this type.
export type RecipeSnapshot = Pick<
  SavedRecipe,
  "id" | "name" | "image" | "ingredients" | "instructions"
>;

export function useSavedRecipes(token: string | null) {
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[]>([]);
  const [savedLoading, setSavedLoading] = useState(false);
  const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());
  const [saveError, setSaveError] = useState("");

  const savedIds = useMemo(
    () => new Set(savedRecipes.map((recipe) => recipe.id)),
    [savedRecipes],
  );

  // Load the full saved list on sign-in; clear it on sign-out.
  useEffect(() => {
    if (!token) {
      setSavedRecipes([]);
      setSavedLoading(false);
      return;
    }

    const controller = new AbortController();
    setSavedLoading(true);

    fetch(`${API_BASE}/api/v1/saved-recipes`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Request failed with ${res.status}`);
        setSavedRecipes((await res.json()) as SavedRecipe[]);
      })
      .catch(() => {
        if (controller.signal.aborted) return;
      })
      .finally(() => {
        if (!controller.signal.aborted) setSavedLoading(false);
      });

    return () => controller.abort();
  }, [token]);

  const toggleSaved = useCallback(
    async (recipe: RecipeSnapshot) => {
      if (!token) return;

      const id = recipe.id;
      const wasSaved = savedIds.has(id);
      const url = `${API_BASE}/api/v1/saved-recipes/${encodeURIComponent(id)}`;

      setPendingIds((prev) => new Set(prev).add(id));
      setSaveError("");

      try {
        if (wasSaved) {
          const res = await fetch(url, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
          });
          if (!res.ok) throw new Error(`Request failed with ${res.status}`);

          setSavedRecipes((prev) => prev.filter((item) => item.id !== id));
        } else {
          const res = await fetch(url, {
            method: "PUT",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: recipe.name,
              image: recipe.image,
              ingredients: recipe.ingredients,
              instructions: recipe.instructions,
            }),
          });
          if (!res.ok) throw new Error(`Request failed with ${res.status}`);

          const saved = (await res.json()) as SavedRecipe;
          setSavedRecipes((prev) =>
            prev.some((item) => item.id === id) ? prev : [saved, ...prev],
          );
        }
      } catch {
        setSaveError("Could not update your saved recipes. Please try again.");
      } finally {
        setPendingIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      }
    },
    [token, savedIds],
  );

  
  return {
    savedRecipes,
    savedLoading,
    isSaved: (id: string) => savedIds.has(id),
    isPending: (id: string) => pendingIds.has(id),
    toggleSaved,
    saveError,
  };
}