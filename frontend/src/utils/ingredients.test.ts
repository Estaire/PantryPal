import { describe, it, expect } from "vitest";
import { combineIngredients } from "./ingredients";

describe("combineIngredients", () => {
  it("splits on commas, semicolons, and newlines", () => {
    expect(combineIngredients([], "eggs; milk,\nbutter")).toEqual([
      "eggs",
      "milk",
      "butter",
    ]);
  });

  it("drops empty entries", () => {
    expect(combineIngredients([], " , ;\n  ,")).toEqual([]);
  });

  it("collapses extra whitespace inside and around entries", () => {
    expect(combineIngredients([], "  chicken   breast  ")).toEqual([
      "chicken breast",
    ]);
  });

  it("does not duplicate ingredients already in the pantry", () => {
    expect(combineIngredients(["rice"], "rice, beans")).toEqual([
      "rice",
      "beans",
    ]);
  });

  it("removes duplicates within the input itself", () => {
    expect(combineIngredients([], "rice, rice, rice")).toEqual(["rice"]);
  });

  it("keeps existing ingredients in their original order", () => {
    expect(combineIngredients(["onion", "garlic"], "carrot")).toEqual([
      "onion",
      "garlic",
      "carrot",
    ]);
  });
});