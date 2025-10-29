"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";

import { getJson, postJson } from "@/lib/api-client";

type ResumeItem = {
  id: string;
  base: boolean;
  original_filename: string | null;
  created_at: string;
  ats_score: number | null;
};

type ResumeDetail = {
  id: string;
  sections: Record<string, unknown> | null;
  ats_score: number | null;
};

export default function ResumesPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const listQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["resumes", userId],
    queryFn: async () => getJson<ResumeItem[]>("/resumes", { userId }),
  });

  const tailorMutation = useMutation({
    mutationFn: async (resumeId: string) =>
      postJson(`/resumes/${resumeId}/tailor`, {}, { userId }),
    onSuccess: () => listQuery.refetch(),
  });

  const optimizeMutation = useMutation({
    mutationFn: async (resumeId: string) =>
      postJson(`/resumes/${resumeId}/optimize`, {}, { userId }),
    onSuccess: () => listQuery.refetch(),
  });

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Resumes</h2>
        <p className="mt-2 text-sm text-slate-300">
          Tailor a resume for a specific role or run ATS optimization to surface suggestions.
        </p>
      </header>

      {listQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading resumes…</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {(listQuery.data ?? []).map((resume) => (
            <article key={resume.id} className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/30 p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200">{resume.original_filename ?? "Resume"}</h3>
                  <p className="text-xs text-slate-500">
                    {resume.base ? "Base resume" : "Tailored variant"} • ATS {resume.ats_score ?? 0}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => tailorMutation.mutate(resume.id)}
                  disabled={tailorMutation.isPending}
                  className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
                >
                  {tailorMutation.isPending ? "Tailoring…" : "Tailor"}
                </button>
                <button
                  type="button"
                  onClick={() => optimizeMutation.mutate(resume.id)}
                  disabled={optimizeMutation.isPending}
                  className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
                >
                  {optimizeMutation.isPending ? "Optimizing…" : "Optimize"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
