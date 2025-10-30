"use client";

import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { useSession } from "next-auth/react";

import { ApiError, getJson } from "@/lib/api-client";

type DigestItem = {
  job_id: string;
  title: string;
  company: string | null;
  location: string | null;
  remote: boolean;
  url: string | null;
  fit_score: number | null;
  why_fit: string | null;
};

type DigestResponse = {
  generated_at: string;
  items: DigestItem[];
};

export default function DigestPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const digestQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["digest", userId],
    queryFn: async () => getJson<DigestResponse>("/notifications/latest/digest", { userId }),
    retry: false,
  });

  const items = digestQuery.data?.items ?? [];
  const generatedAtLabel = digestQuery.data
    ? format(new Date(digestQuery.data.generated_at), "PPpp")
    : null;

  const error = digestQuery.error as ApiError | null;

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Latest Digest</h2>
        <p className="mt-2 text-sm text-slate-300">
          A snapshot of the top matches from your most recent scheduled search.
        </p>
        {generatedAtLabel && (
          <p className="mt-3 text-xs text-slate-500">Generated {generatedAtLabel}</p>
        )}
      </div>

      {digestQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading your latest digest…</p>
      ) : error?.status === 404 ? (
        <p className="text-sm text-slate-400">
          No digest available yet. Check back after your first scheduled run completes.
        </p>
      ) : error ? (
        <p className="text-sm text-rose-300">Unable to load digest right now. Please try again later.</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-400">Nothing new to review—great job staying on top of things!</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <article
              key={item.job_id}
              className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/30 p-5"
            >
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-sm font-semibold text-slate-200">{item.title}</h3>
                {typeof item.fit_score === "number" && (
                  <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-200">
                    Fit {item.fit_score}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">
                {[item.company, item.location, item.remote ? "Remote" : null].filter(Boolean).join(" • ")}
              </p>
              {item.why_fit && (
                <p className="text-xs text-slate-400">
                  <span className="font-semibold text-slate-300">Why fit:</span> {item.why_fit}
                </p>
              )}
              <div className="flex items-center gap-2">
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full border border-accent px-3 py-1 text-[11px] text-accent transition hover:border-accent hover:bg-accent/10"
                  >
                    View role
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
