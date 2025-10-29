"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { useSession } from "next-auth/react";

import { getJson, postJson } from "@/lib/api-client";

type NotificationItem = {
  id: string;
  kind: string;
  payload: Record<string, unknown> | null;
  read_at: string | null;
  created_at: string;
};

function resolveTitle(notification: NotificationItem): string {
  switch (notification.kind) {
    case "daily_digest":
      return "Daily Digest";
    case "resume_tailored":
      return "Resume tailored and ready";
    case "resume_optimized":
      return "Resume optimization complete";
    default:
      return notification.kind.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
  }
}

export default function NotificationsPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const notificationsQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["notifications", userId],
    queryFn: async () => getJson<NotificationItem[]>("/notifications", { userId }),
  });

  const markReadMutation = useMutation({
    mutationFn: async (notificationId: string) =>
      postJson(`/notifications/${notificationId}/read`, {}, { userId }),
    onSuccess: () => notificationsQuery.refetch(),
  });

  const items = notificationsQuery.data ?? [];

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Notifications</h2>
        <p className="mt-2 text-sm text-slate-300">
          Stay updated on digests, resume generation, and other activity from your Vanta agents.
        </p>
      </header>

      {notificationsQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading notifications…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-400">You&apos;re all caught up.</p>
      ) : (
        <div className="space-y-3">
          {items.map((notification) => {
            const createdAt = new Date(notification.created_at);
            const read = Boolean(notification.read_at);
            return (
              <article
                key={notification.id}
                className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/30 p-5 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <h3 className="text-sm font-semibold text-slate-200">
                    {resolveTitle(notification)}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {formatDistanceToNow(createdAt, { addSuffix: true })}
                  </p>
                  {notification.payload && Object.keys(notification.payload).length > 0 && (
                    <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">
                      {JSON.stringify(notification.payload, null, 2)}
                    </pre>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex h-2 w-2 rounded-full ${
                      read ? "bg-slate-600" : "bg-emerald-400"
                    }`}
                    aria-hidden
                  />
                  <button
                    type="button"
                    disabled={read || markReadMutation.isPending}
                    onClick={() => markReadMutation.mutate(notification.id)}
                    className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-accent hover:text-accent disabled:cursor-default disabled:opacity-60"
                  >
                    {read ? "Read" : markReadMutation.isPending ? "Marking…" : "Mark as read"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
