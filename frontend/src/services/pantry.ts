
import { API_BASE } from "../config";

interface PantryResponse {
  ingredients: string[];
}

async function pantryRequest(
  token: string,
  method: "GET" | "PUT",
  ingredients?: string[],
): Promise<PantryResponse> {
  const response = await fetch(`${API_BASE}/api/v1/pantry`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    ...(method === "PUT"
      ? { body: JSON.stringify({ ingredients }) }
      : {}),
  });

  if (!response.ok) {
    let message = "Could not synchronize your pantry.";

    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Keep the fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<PantryResponse>;
}

export function fetchPantry(token: string): Promise<PantryResponse> {
  return pantryRequest(token, "GET");
}

export function savePantry(
  token: string,
  ingredients: string[],
): Promise<PantryResponse> {
  return pantryRequest(token, "PUT", ingredients);
}
