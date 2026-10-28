
import { useEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { fetchPantry, savePantry } from "../services/pantry";
import type { User } from "../services/auth";

interface UsePersistentPantryOptions {
  user: User | null;
  token: string | null;
  authLoading: boolean;
  ingredients: string[];
  setIngredients: Dispatch<SetStateAction<string[]>>;
  onSignedOut: () => void;
}

export function usePersistentPantry({
  user,
  token,
  authLoading,
  ingredients,
  setIngredients,
  onSignedOut,
}: UsePersistentPantryOptions) {
  const [loadedUserId, setLoadedUserId] = useState<number | null>(null);
  const [syncError, setSyncError] = useState("");
  const previousUserId = useRef<number | null>(null);

  const userId = user?.id ?? null;

  // Load the pantry whenever the authenticated account changes.
  useEffect(() => {
    if (authLoading) return;

    if (userId === null || !token) {
      if (previousUserId.current !== null) {
        setIngredients([]);
        onSignedOut();
      }

      previousUserId.current = null;
      setLoadedUserId(null);
      setSyncError("");
      return;
    }

    let cancelled = false;

    previousUserId.current = userId;
    setLoadedUserId(null);
    setSyncError("");

    fetchPantry(token)
      .then(({ ingredients: savedIngredients }) => {
        if (cancelled) return;

        setIngredients(savedIngredients);
        setLoadedUserId(userId);
      })
      .catch((error: unknown) => {
        if (cancelled) return;

        setSyncError(
          error instanceof Error
            ? error.message
            : "Could not load your saved pantry.",
        );
      });

    return () => {
      cancelled = true;
    };
  }, [
    authLoading,
    userId,
    token,
    setIngredients,
    onSignedOut,
  ]);

  // Save changes only after the current user's pantry has loaded.
  useEffect(() => {
    if (
      authLoading ||
      userId === null ||
      !token ||
      loadedUserId !== userId
    ) {
      return;
    }

    const ingredientsToSave = [...ingredients];
    let cancelled = false;

    const timer = window.setTimeout(() => {
      savePantry(token, ingredientsToSave)
        .then(() => {
          if (!cancelled) setSyncError("");
        })
        .catch((error: unknown) => {
          if (cancelled) return;

          setSyncError(
            error instanceof Error
              ? error.message
              : "Could not save your pantry.",
          );
        });
    }, 500);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [authLoading, userId, token, loadedUserId, ingredients]);

  return {
    pantryLoaded: userId !== null && loadedUserId === userId,
    syncError,
  };
}
