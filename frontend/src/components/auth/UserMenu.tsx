
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import AuthModal from "./AuthModal";

export default function UserMenu() {
  const { user, logout, authLoading } = useAuth();
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(
    null,
  );

  return (
    <>
      <div className="flex items-center gap-3">
        {authLoading ? (
          <span
            className="text-sm text-stone-500"
            aria-live="polite"
          >
            Checking account...
          </span>
        ) : user ? (
          <>
            <span
              className="hidden max-w-48 truncate text-sm text-stone-600 sm:block"
              title={user.email}
            >
              {user.email}
            </span>

            <button
              type="button"
              onClick={logout}
              className="rounded-full border border-stone-300 px-3 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100"
            >
              Sign Out
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => setAuthMode("login")}
              className="rounded-full px-3 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100"
            >
              Sign in
            </button>

            <button
              type="button"
              onClick={() => setAuthMode("register")}
              className="rounded-full bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800"
            >
              Create account
            </button>
          </>
        )}
      </div>

      {authMode && (
        <AuthModal
          initialMode={authMode}
          onClose={() => setAuthMode(null)}
        />
      )}
    </>
  );
}
