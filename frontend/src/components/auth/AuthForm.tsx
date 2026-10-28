
import { useState, type SubmitEvent } from "react";

export type AuthMode = "login" | "register";

interface AuthFormProps {
  mode: AuthMode;
  onSubmit: (email: string, password: string) => Promise<void>;
  onModeChange: (mode: AuthMode) => void;
}

export default function AuthForm({
  mode,
  onSubmit,
  onModeChange,
}: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Authentication failed. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const isRegistering = mode === "register";

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          {isRegistering ? "Create your account" : "Welcome back"}
        </h2>
        <p className="mt-2 text-sm leading-6 text-stone-600">
          {isRegistering
            ? "Create an account to get started with PantryPal."
            : "Sign in to your PantryPal account."}
        </p>
      </div>

      {error && (
        <p
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </p>
      )}

      <div>
        <label
          htmlFor="auth-email"
          className="mb-2 block text-sm font-medium text-stone-700"
        >
          Email address
        </label>
        <input
          id="auth-email"
          type="email"
          autoComplete="email"
          required
          maxLength={254}
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
        />
      </div>

      <div>
        <label
          htmlFor="auth-password"
          className="mb-2 block text-sm font-medium text-stone-700"
        >
          Password
        </label>
        <input
          id="auth-password"
          type="password"
          autoComplete={
            isRegistering ? "new-password" : "current-password"
          }
          required
          minLength={isRegistering ? 8 : 1}
          maxLength={128}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder={
            isRegistering ? "At least 8 characters" : "Your password"
          }
          className="w-full rounded-xl border border-stone-300 px-4 py-3 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
        />
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-xl bg-emerald-700 px-5 py-3 font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {submitting
          ? "Please wait..."
          : isRegistering
            ? "Create account"
            : "Sign in"}
      </button>

      <p className="text-center text-sm text-stone-600">
        {isRegistering
          ? "Already have an account?"
          : "Don't have an account?"}{" "}
        <button
          type="button"
          onClick={() =>
            onModeChange(isRegistering ? "login" : "register")
          }
          className="font-semibold text-emerald-700 hover:text-emerald-900"
        >
          {isRegistering ? "Sign in" : "Create one"}
        </button>
      </p>
    </form>
  );
}
