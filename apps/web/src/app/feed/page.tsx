"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { useState } from "react";

import { getJson, postJson } from "@/lib/api-client";

type FeedItem = {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  remote: boolean;
  url: string;
  tags: string[];
  fit_score?: number | null;
  fit_factors?: Record<string, number>;
  why_fit?: string | null;
};

type FeedResponse = {
  items: FeedItem[];
  page: number;
  limit: number;
  total: number;
};

export default function FeedPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;
  const [filters, setFilters] = useState({ location: "", remoteOnly: false });

  const feedQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["feed", filters, userId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.location.trim()) {
        params.set("location", filters.location.trim());
      }
      if (filters.remoteOnly) {
        params.set("remote_only", "true");
      }
      const search = params.size ? `?${params.toString()}` : "";
      return getJson<FeedResponse>(`/feed/jobs${search}`, { userId });
    },
  });

  const hideMutation = useMutation({
    mutationFn: async (jobId: string) =>
      postJson(`/feed/jobs/${jobId}/hide`, {}, { userId }),
    onSuccess: () => feedQuery.refetch(),
  });

  const trackMutation = useMutation({
    mutationFn: async (jobId: string) =>
      postJson("/applications/", { job_posting_id: jobId }, { userId }),
  });

  const items = feedQuery.data?.items ?? [];

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Job Feed</h2>
        <p className="mt-2 text-sm text-slate-300">
          Fresh roles pulled from integrated providers. Filter to narrow your focus and hide the
          ones you do not want to see again.
        </p>
      </div>

      <form
        className="flex flex-wrap items-end gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6"
        onSubmit={(event) => {
          event.preventDefault();
          feedQuery.refetch();
        }}
      >
        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Location</span>
          <input
            type="text"
            value={filters.location}
            onChange={(event) => setFilters((prev) => ({ ...prev, location: event.target.value }))}
            className="w-64 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
            placeholder="Remote, Toronto, NYC..."
          />
        </label>

        <label className="flex items-center gap-2 text-sm text-slate-200">
          <input
            type="checkbox"
            checked={filters.remoteOnly}
            onChange={(event) => setFilters((prev) => ({ ...prev, remoteOnly: event.target.checked }))}
          />
          Remote only
        </label>

        <button
          type="submit"
          className="rounded-full bg-accent px-6 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300"
        >
          Apply filters
        </button>
      </form>

      <div className="space-y-4">
        {feedQuery.isLoading && <p className="text-sm text-slate-400">Loading jobs…</p>}
        {!feedQuery.isLoading && items.length === 0 && (
          <p className="text-sm text-slate-400">No jobs found with the current filters.</p>
        )}

        {items.map((job) => (
          <article
            key={job.id}
            className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/30 p-6 md:flex-row md:items-center md:justify-between"
          >
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-semibold text-slate-200">{job.title}</h3>
                {typeof job.fit_score === "number" && (
                  <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-200">
                    Fit {job.fit_score}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-400">
                {job.company ? `${job.company} • ` : ""}
                {job.location ?? "Location unknown"}
                {job.remote ? " • Remote" : ""}
              </p>
              {job.tags.length > 0 && (
                <ul className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
                  {job.tags.map((tag) => (
                    <li key={tag} className="rounded-full border border-slate-700 px-3 py-1">
                      {tag}
                    </li>
                  ))}
                </ul>
              )}
              {job.why_fit && (
                <p className="text-xs text-slate-400">
                  <span className="font-semibold text-slate-300">Why fit:</span> {job.why_fit}
                </p>
              )}
            </div>

            <div className="flex items-center gap-3">
              <a
                href={job.url}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-accent px-4 py-2 text-xs font-semibold text-accent transition hover:bg-accent hover:text-slate-950"
              >
                View role
              </a>
              <button
                type="button"
                onClick={() => trackMutation.mutate(job.id)}
                disabled={trackMutation.isPending}
                className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
              >
                {trackMutation.isPending ? "Tracking…" : "Track"}
              </button>
              <button
                type="button"
                onClick={() => hideMutation.mutate(job.id)}
                disabled={hideMutation.isPending}
                className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-rose-400 hover:text-rose-300"
              >
                {hideMutation.isPending ? "Hiding…" : "Hide"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
