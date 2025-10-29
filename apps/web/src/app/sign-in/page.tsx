"use client";

import { useState, useTransition } from "react";
import { signIn } from "next-auth/react";

export default function SignInPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    startTransition(async () => {
      const result = await signIn("credentials", {
        email,
        redirect: true,
        callbackUrl: "/onboarding",
      });
      if (result?.error) {
        setError("Unable to sign in. Please verify your email and try again.");
      }
    });
  };

  return (
    <section className="mx-auto max-w-md space-y-6 rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Sign in</h2>
        <p className="text-sm text-slate-400">Use your email to continue to your job search workspace.</p>
      </div>

      <form className="space-y-4" onSubmit={onSubmit}>
        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
            placeholder="you@example.com"
          />
        </label>
        {error && <p className="text-xs text-rose-400">{error}</p>}
        <button
          type="submit"
          disabled={isPending}
          className="w-full rounded-full bg-accent px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {isPending ? "Signing in..." : "Continue"}
        </button>
      </form>
    </section>
  );
}
