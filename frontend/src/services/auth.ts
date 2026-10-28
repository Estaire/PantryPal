import { API_BASE } from "../config";

export interface User {
  id: number;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface AuthCredentials {
  email: string;
  password: string;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1/auth${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = "Something went wrong. Please try again.";

    try {
      const data: unknown = await response.json();

      if (
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        typeof data.detail === "string"
      ) {
        message = data.detail;
      } else if (
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        Array.isArray(data.detail)
      ) {
        message = data.detail
          .map((item: { msg?: string }) => item.msg ?? "Invalid input")
          .join(" ");
      }
    } catch {
      // Keep the fallback message for non-JSON responses.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function register(credentials: AuthCredentials): Promise<User> {
  return request<User>("/register", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export function login(
  credentials: AuthCredentials,
): Promise<AuthResponse> {
  return request<AuthResponse>("/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export function getCurrentUser(token: string): Promise<User> {
  return request<User>("/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}
