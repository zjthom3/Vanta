"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo } from "react";
import { useSession, signOut } from "next-auth/react";

import { getJson } from "@/lib/api-client";

type NotificationSummary = {
  id: string;
  read_at: string | null;
};

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

  const userId = session.user?.id;
  const notificationsQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["notifications", userId],
    queryFn: async () => getJson<NotificationSummary[]>("/notifications", { userId }),
    staleTime: 30_000,
  });

  const unreadCount =
    notificationsQuery.data?.reduce((total, notification) => total + (notification.read_at ? 0 : 1), 0) ?? 0;

  return (
    <div className="flex items-center gap-3">
      <Link
        href="/notifications"
        className="relative rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300 transition hover:border-accent"
      >
        Notifications
        {unreadCount > 0 && (
          <span className="ml-2 inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-accent px-1 text-[10px] font-semibold text-slate-950">
            {unreadCount}
          </span>
        )}
      </Link>
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
