import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  register as registerRequest,
  type User,
} from "../services/auth";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  authLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "pantrypal_access_token";

function readStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(readStoredToken);
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(Boolean(token));

  const saveToken = useCallback((nextToken: string | null) => {
    try {
      if (nextToken) {
        localStorage.setItem(TOKEN_KEY, nextToken);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }
    } catch {
    }

    setToken(nextToken);
  }, []);

  const logout = useCallback(() => {
    saveToken(null);
    setUser(null);
    setAuthLoading(false);
  }, [saveToken]);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setAuthLoading(false);
      return;
    }

    let cancelled = false;

    setAuthLoading(true);

    getCurrentUser(token)
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser);
        }
      })
      .catch(() => {
        if (!cancelled) {
          logout();
        }
      })
      .finally(() => {
        if (!cancelled) {
          setAuthLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token, logout]);

  useEffect(() => {
    function handleStorage(event: StorageEvent) {
      if (event.key === TOKEN_KEY && event.newValue === null) {
        setToken(null);
      }
    }

    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);
  
  const login = useCallback(
    async (email: string, password: string) => {
      const result = await loginRequest({
        email: email.trim(),
        password,
      });

      const currentUser = await getCurrentUser(result.access_token);

      saveToken(result.access_token);
      setUser(currentUser);
    },
    [saveToken],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      await registerRequest({
        email: email.trim(),
        password,
      });

      await login(email, password);
    },
    [login],
  );

  return (
    <AuthContext.Provider
      value={{ user, token, authLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
