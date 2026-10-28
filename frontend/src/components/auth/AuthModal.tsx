
import { useEffect, useState } from "react";
import AuthForm, { type AuthMode } from "./AuthForm";
import { useAuth } from "../../context/AuthContext";

interface AuthModalProps {
  initialMode: AuthMode;
  onClose: () => void;
}

export default function AuthModal({
  initialMode,
  onClose,
}: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const { login, register } = useAuth();

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  async function handleSubmit(email: string, password: string) {
    if (mode === "register") {
      await register(email, password);
    } else {
      await login(email, password);
    }

    onClose();
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/50 p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-dialog-title"
        className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl sm:p-8"
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close authentication dialog"
          className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-full text-xl text-stone-500 hover:bg-stone-100 hover:text-stone-900"
        >
          ×
        </button>

        <div id="auth-dialog-title" className="sr-only">
          {mode === "register" ? "Create account" : "Sign in"}
        </div>

        <div className="mb-6 text-xl font-bold tracking-tight">
          PantryPal<span className="text-emerald-600">.</span>
        </div>

        <AuthForm
          mode={mode}
          onSubmit={handleSubmit}
          onModeChange={setMode}
        />
      </section>
    </div>
  );
}
