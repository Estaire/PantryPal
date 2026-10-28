
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import type { Recipe } from "./components/RecipeCard";

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

function mockFetchResponse(
  data: unknown,
  options: { ok?: boolean; status?: number } = {},
): Response {
  return {
    ok: options.ok ?? true,
    status: options.status ?? 200,
    json: async () => data,
  } as Response;
}

async function enterIngredients(
  user: ReturnType<typeof userEvent.setup>,
  value: string,
) {
  await user.type(
    screen.getByRole("textbox", {
      name: /what ingredients do you have/i,
    }),
    value,
  );

  await user.click(
    screen.getByRole("button", { name: /find recipes/i }),
  );
}

describe("PantryPal", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        mockFetchResponse([mockRecipe]),
      ),
    );
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("commits unique ingredients and searches in one action", async () => {
    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "Chicken, rice, CHICKEN");

    expect(
      await screen.findByRole("button", { name: "Remove chicken" }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: "Remove rice" }),
    ).toBeInTheDocument();

    expect(
      screen.getAllByRole("button", { name: "Remove chicken" }),
    ).toHaveLength(1);

    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("finds and displays recipes from the entered ingredients", async () => {
    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken, rice");

    expect(
      await screen.findByRole("heading", {
        name: "Chicken and Rice",
      }),
    ).toBeInTheDocument();

    expect(screen.getByText("100% match")).toBeInTheDocument();

    expect(fetch).toHaveBeenCalledTimes(1);

    const requestedUrl = String(
      vi.mocked(fetch).mock.calls[0][0],
    );

    expect(requestedUrl).toContain("/api/v1/recipes?");
    expect(requestedUrl).toContain("ingredients=chicken");
    expect(requestedUrl).toContain("ingredients=rice");
  });

  it("shows a message when no recipes are found", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockFetchResponse([]),
    );

    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "dragon fruit");

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent(/no recipes found/i);
  });

  it("shows a network error and allows the user to retry", async () => {
    vi.mocked(fetch)
      .mockRejectedValueOnce(new Error("Network unavailable"))
      .mockResolvedValueOnce(mockFetchResponse([mockRecipe]));

    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Network unavailable",
    );

    const searchButton = screen.getByRole("button", {
      name: /find recipes/i,
    });

    expect(searchButton).toBeEnabled();

    await user.click(searchButton);

    expect(
      await screen.findByRole("heading", {
        name: "Chicken and Rice",
      }),
    ).toBeInTheDocument();

    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("does not call the API when there are no ingredients", async () => {
    const user = userEvent.setup();

    render(<App />);

    await user.click(
      screen.getByRole("button", { name: /find recipes/i }),
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /enter at least one ingredient/i,
    );

    expect(fetch).not.toHaveBeenCalled();
  });

  it("allows an ingredient to be removed from the pantry", async () => {
    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken, rice");

    const chickenRemoveButton = await screen.findByRole("button", {
      name: "Remove chicken",
    });

    await user.click(chickenRemoveButton);

    expect(
      screen.queryByRole("button", { name: "Remove chicken" }),
    ).not.toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: "Remove rice" }),
    ).toBeInTheDocument();
  });

  it("shows the API error detail when a request fails", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockFetchResponse(
        { detail: "Recipe provider unavailable" },
        { ok: false, status: 502 },
      ),
    );

    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Recipe provider unavailable",
    );

    expect(
      screen.getByRole("button", { name: /find recipes/i }),
    ).toBeEnabled();
  });

  it("handles an unexpected API response shape", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockFetchResponse({ recipes: [mockRecipe] }),
    );

    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /unexpected recipe response/i,
    );

    expect(
      screen.queryByRole("heading", { name: "Chicken and Rice" }),
    ).not.toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /find recipes/i }),
    ).toBeEnabled();
  });

  it("keeps existing pantry ingredients when adding new ones", async () => {
    const user = userEvent.setup();

    render(<App />);

    await enterIngredients(user, "chicken, rice");

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });

    const input = screen.getByRole("textbox", {
      name: /what ingredients do you have/i,
    });

    await user.type(input, "milk");

    await user.click(
      screen.getByRole("button", { name: /find recipes/i }),
    );

    expect(
      await screen.findByRole("button", { name: "Remove milk" }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: "Remove chicken" }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: "Remove rice" }),
    ).toBeInTheDocument();

    expect(fetch).toHaveBeenCalledTimes(2);

    const latestUrl = String(
      vi.mocked(fetch).mock.calls[1][0],
    );

    expect(latestUrl).toContain("ingredients=chicken");
    expect(latestUrl).toContain("ingredients=rice");
    expect(latestUrl).toContain("ingredients=milk");
  });
});
