// @vitest-environment jsdom
import { afterEach, describe, it, expect, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import RecipeDetailPanel from "./components/RecipeDetailPanel";
import type { Recipe } from "./components/RecipeCard";

afterEach(cleanup);

const recipe: Recipe = {
  id: "52818",
  name: "Chicken Rice",
  image: "",
  ingredients: [
    { name: "Chicken Breast", measure: "200g", canonical: "chicken" },
    { name: "Rice", measure: "1 cup", canonical: "rice" },
  ],
  instructions: "Cook the rice. Add the chicken.",
  match_score: 100,
  missing_ingredients: [],
  status: "ready_to_cook",
  substitutions: {},
  missing_count: 0,
  recommendation_category: "ready_to_cook",
  available_substitutions: {},
};

function renderPanel(overrides: Partial<React.ComponentProps<typeof RecipeDetailPanel>> = {}) {
  return render(
    <RecipeDetailPanel
      recipe={recipe}
      onClose={vi.fn()}
      pantryIngredients={[]}
      onTogglePantryIngredient={vi.fn()}
      isSaved={false}
      isSavePending={false}
      onToggleSave={null}
      saveError=""
      {...overrides}
    />,
  );
}

describe("RecipeDetailPanel ingredient checkboxes", () => {
  it("checks an ingredient when its canonical name is in the pantry", () => {
    renderPanel({ pantryIngredients: ["chicken"] });

    const [chicken] = screen.getAllByRole("checkbox") as HTMLInputElement[];
    expect(chicken.checked).toBe(true);
  });

  it("does not check an ingredient when only the raw name is in the pantry", () => {
    renderPanel({ pantryIngredients: ["chicken breast"] });

    const [chicken] = screen.getAllByRole("checkbox") as HTMLInputElement[];
    expect(chicken.checked).toBe(false);
  });

  it("leaves unrelated ingredients unchecked", () => {
    renderPanel({ pantryIngredients: ["chicken"] });

    const [, rice] = screen.getAllByRole("checkbox") as HTMLInputElement[];
    expect(rice.checked).toBe(false);
  });
});

describe("RecipeDetailPanel save button", () => {
  it("shows a sign-in prompt when there is no save handler", () => {
    renderPanel({ onToggleSave: null });

    expect(screen.getByText("Sign in to save")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /save recipe/i })).toBeNull();
  });

  it("shows the saved state when the recipe is saved", () => {
    renderPanel({ isSaved: true, onToggleSave: vi.fn() });

    expect(screen.getByRole("button", { name: /saved/i })).toBeTruthy();
  });

  it("offers to save when the recipe is not yet saved", () => {
    renderPanel({ isSaved: false, onToggleSave: vi.fn() });

    expect(screen.getByRole("button", { name: /save recipe/i })).toBeTruthy();
  });
});