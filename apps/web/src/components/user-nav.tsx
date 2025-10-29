"use client";

import { signOut } from "next-auth/react";
import Link from "next/link";
import { useMemo } from "react";
import { useSession } from "next-auth/react";

export function UserNav() {
  const { data: session, status } = useSession();

  const initials = useMemo(() => {
    const email = session?.user?.email ?? "";
    const [name] = email.split("@");
    return name ? name[0]?.toUpperCase() : "U";
  }, [session?.user?.email]);

  if (status === "loading") {
    return <span className="text-xs text-slate-500">Loading…</span>;
  }

  if (!session?.user) {
    return (
      <Link
        href="/sign-in"
        className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300 transition hover:border-accent"
      >
        Sign in
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold">
        {initials}
      </span>
      <button
        type="button"
        onClick={() => signOut({ callbackUrl: "/sign-in" })}
        className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300 transition hover:border-accent"
      >
        Sign out
      </button>
    </div>
  );
}
