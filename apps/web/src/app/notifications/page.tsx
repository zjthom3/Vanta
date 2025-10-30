"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { useSession } from "next-auth/react";
import { useMemo, useState } from "react";

import { getJson, postJson } from "@/lib/api-client";

type NotificationItem = {
  id: string;
  kind: string;
  payload: Record<string, unknown> | null;
  read_at: string | null;
  created_at: string;
};

type DigestItem = {
  job_id: string;
  title: string;
  company: string | null;
  location: string | null;
  remote: boolean;
  url: string | null;
  fit_score: number | null;
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
  const [activeFilter, setActiveFilter] = useState<"all" | "unread" | "digest" | "resume">("all");

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

  const trackMutation = useMutation({
    mutationFn: async (jobId: string) =>
      postJson("/applications/", { job_posting_id: jobId }, { userId }),
  });

  const hideMutation = useMutation({
    mutationFn: async (jobId: string) => postJson(`/feed/jobs/${jobId}/hide`, {}, { userId }),
  });

  const items = notificationsQuery.data ?? [];
  const filteredItems = useMemo(() => {
    switch (activeFilter) {
      case "unread":
        return items.filter((notification) => !notification.read_at);
      case "digest":
        return items.filter((notification) => notification.kind === "daily_digest");
      case "resume":
        return items.filter(
          (notification) => notification.kind === "resume_tailored" || notification.kind === "resume_optimized",
        );
      default:
        return items;
    }
  }, [activeFilter, items]);

  const filterOptions: Array<{ label: string; value: typeof activeFilter; count: number }> = [
    { label: "All", value: "all", count: items.length },
    { label: "Unread", value: "unread", count: items.filter((item) => !item.read_at).length },
    { label: "Digests", value: "digest", count: items.filter((item) => item.kind === "daily_digest").length },
    { label: "Resumes", value: "resume", count: items.filter((item) => item.kind.startsWith("resume_")).length },
  ];

  const currentTrackJob = (trackMutation.variables as string | undefined) ?? null;
  const currentHideJob = (hideMutation.variables as string | undefined) ?? null;

  const renderContent = (notification: NotificationItem) => {
    const payload = notification.payload ?? {};
    switch (notification.kind) {
      case "daily_digest": {
        const items = Array.isArray(payload["items"]) ? (payload["items"] as DigestItem[]) : [];
        if (items.length === 0) {
          return <p className="mt-2 text-xs text-slate-400">No new roles in the latest digest.</p>;
        }
        return (
          <div className="mt-3 space-y-3">
            {items.map((item) => {
              const jobId = item.job_id;
              const tracking = trackMutation.isPending && currentTrackJob === jobId;
              const hiding = hideMutation.isPending && currentHideJob === jobId;
              return (
                <div
                  key={`${notification.id}-${jobId}`}
                  className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-xs text-slate-300"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-slate-200">{item.title}</p>
                      <p className="text-slate-400">
                        {[item.company, item.location, item.remote ? "Remote" : null].filter(Boolean).join(" • ")}
                      </p>
                    </div>
                    {typeof item.fit_score === "number" && (
                      <span className="rounded-full bg-slate-900 px-2 py-1 text-[11px] text-accent">
                        Fit {item.fit_score}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-full border border-slate-700 px-3 py-1 text-[11px] text-accent transition hover:border-accent"
                      >
                        View posting
                      </a>
                    )}
                    {jobId && (
                      <>
                        <button
                          type="button"
                          className="rounded-full border border-slate-700 px-3 py-1 text-[11px] text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300 disabled:cursor-default disabled:opacity-60"
                          disabled={tracking || !userId}
                          onClick={() => trackMutation.mutate(jobId)}
                        >
                          {tracking ? "Tracking…" : "Track"}
                        </button>
                        <button
                          type="button"
                          className="rounded-full border border-slate-700 px-3 py-1 text-[11px] text-slate-300 transition hover:border-rose-400 hover:text-rose-300 disabled:cursor-default disabled:opacity-60"
                          disabled={hiding || !userId}
                          onClick={() => hideMutation.mutate(jobId)}
                        >
                          {hiding ? "Hiding…" : "Hide"}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        );
      }
      case "resume_tailored": {
        const resumeId = typeof payload["resume_id"] === "string" ? payload["resume_id"] : null;
        const jobPostingId = typeof payload["job_posting_id"] === "string" ? payload["job_posting_id"] : null;
        return (
          <p className="mt-2 text-xs text-slate-400">
            Tailored resume {resumeId ? <span className="font-mono text-slate-200">{resumeId}</span> : "ready"}{" "}
            {jobPostingId ? (
              <>
                for job <span className="font-mono text-slate-200">{jobPostingId}</span>
              </>
            ) : (
              ""
            )}
          </p>
        );
      }
      case "resume_optimized": {
        const resumeId = typeof payload["resume_id"] === "string" ? payload["resume_id"] : null;
        const score = typeof payload["ats_score"] === "number" ? payload["ats_score"] : null;
        return (
          <p className="mt-2 text-xs text-slate-400">
            Resume {resumeId ? <span className="font-mono text-slate-200">{resumeId}</span> : ""} optimized
            {score !== null ? ` • ATS score ${score}` : ""}
          </p>
        );
      }
      default:
        if (Object.keys(payload).length === 0) {
          return null;
        }
        return (
          <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">
            {JSON.stringify(payload, null, 2)}
          </pre>
        );
    }
  };

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Notifications</h2>
        <p className="mt-2 text-sm text-slate-300">
          Stay updated on digests, resume generation, and other activity from your Vanta agents.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-2">
        {filterOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => setActiveFilter(option.value)}
            className={`flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-medium transition ${
              activeFilter === option.value
                ? "border-accent bg-accent text-slate-950"
                : "border-slate-700 text-slate-300 hover:border-accent hover:text-accent"
            }`}
          >
            <span>{option.label}</span>
            <span
              className={`inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full ${
                activeFilter === option.value ? "bg-slate-900 text-accent" : "bg-slate-800 text-slate-400"
              } px-1 text-[10px]`}
            >
              {option.count}
            </span>
          </button>
        ))}
      </div>

      {notificationsQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading notifications…</p>
      ) : filteredItems.length === 0 ? (
        <p className="text-sm text-slate-400">You&apos;re all caught up.</p>
      ) : (
        <div className="space-y-3">
          {filteredItems.map((notification) => {
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
                  {renderContent(notification)}
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
