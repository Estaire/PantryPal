
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RecipeCard, { type Recipe } from "./components/RecipeCard";

const mockRecipe: Recipe = {
  id: "recipe-1",
  name: "Chicken and Rice",
  image: "https://example.com/chicken-rice.jpg",
  ingredients: [
    { name: "chicken", measure: "", canonical: "chicken" },
    { name: "rice", measure: "", canonical: "rice" },
  ],
  instructions: "Cook the chicken. Add rice and simmer.",
  match_score: 100,
  missing_ingredients: [],
  status: "ready_to_cook",
  substitutions: {},
  missing_count: 0,
  recommendation_category: "ready_to_cook",
  available_substitutions: {},
};

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("RecipeCard", () => {
  it("displays the recipe name and match score", () => {
    render(
      <RecipeCard recipe={mockRecipe} onViewDetails={vi.fn()} />,
    );

    expect(
      screen.getByRole("heading", { name: "Chicken and Rice" }),
    ).toBeInTheDocument();

    expect(screen.getByText("100% match")).toBeInTheDocument();
    expect(screen.getByText("Ready to cook")).toBeInTheDocument();
  });

  it("displays the recipe image with descriptive alt text", () => {
    render(
      <RecipeCard recipe={mockRecipe} onViewDetails={vi.fn()} />,
    );

    expect(
      screen.getByRole("img", { name: "Chicken and Rice" }),
    ).toHaveAttribute(
      "src",
      "https://example.com/chicken-rice.jpg",
    );
  });

  it("shows a fallback when the recipe has no image", () => {
    render(
      <RecipeCard
        recipe={{ ...mockRecipe, image: "" }}
        onViewDetails={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("img", {
        name: "No recipe image available",
      }),
    ).toBeInTheDocument();
  });

  it("shows missing ingredients", () => {
    render(
      <RecipeCard
        recipe={{
          ...mockRecipe,
          missing_ingredients: ["milk", "butter"],
          missing_count: 2,
          status: "missing_ingredients",
          recommendation_category: "almost_there",
        }}
        onViewDetails={vi.fn()}
      />,
    );

    expect(screen.getByText("2 missing")).toBeInTheDocument();
    expect(screen.getByText("Missing: milk, butter")).toBeInTheDocument();
  });

  it("shows compact indicators for available swaps and alternatives", () => {
    render(
      <RecipeCard
        recipe={{
          ...mockRecipe,
          available_substitutions: {
            butter: ["olive oil", "margarine"],
          },
          substitutions: {
            milk: ["oat milk", "soy milk"],
            cream: ["yogurt"],
          },
        }}
        onViewDetails={vi.fn()}
      />,
    );

    expect(screen.getByText("↔ 2 available swaps")).toBeInTheDocument();
    expect(screen.getByText("+3 alternatives")).toBeInTheDocument();

    expect(
      screen.queryByText("Substitutions you can use"),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText("Possible substitutes"),
    ).not.toBeInTheDocument();
  });

  it("does not show substitution indicators when there are no alternatives", () => {
    render(
      <RecipeCard recipe={mockRecipe} onViewDetails={vi.fn()} />,
    );

    expect(screen.queryByText(/available swaps/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/alternatives/i)).not.toBeInTheDocument();
  });

  it("opens the selected recipe details when View recipe is clicked", async () => {
    const user = userEvent.setup();
    const onViewDetails = vi.fn();

    render(
      <RecipeCard
        recipe={mockRecipe}
        onViewDetails={onViewDetails}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: /view recipe/i }),
    );

    expect(onViewDetails).toHaveBeenCalledTimes(1);
    expect(onViewDetails).toHaveBeenCalledWith(mockRecipe);
  });

  it("shows a fallback for an invalid match score", () => {
    render(
      <RecipeCard
        recipe={{
          ...mockRecipe,
          match_score: Number.NaN,
        }}
        onViewDetails={vi.fn()}
      />,
    );

    expect(screen.getByText("Match unavailable")).toBeInTheDocument();
  });

  it("uses a fallback when the recipe name is empty", () => {
    render(
      <RecipeCard
        recipe={{ ...mockRecipe, name: "" }}
        onViewDetails={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Untitled recipe" }),
    ).toBeInTheDocument();
  });
});
