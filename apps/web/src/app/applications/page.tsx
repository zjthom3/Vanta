"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import { useSession } from "next-auth/react";

import { getJson, patchJson } from "@/lib/api-client";

type ApplicationItem = {
  id: string;
  title: string;
  company: string | null;
  stage: string;
  url: string | null;
  tasks: Array<{ id: string; title: string; type?: string | null }>;
};

type ApplicationsResponse = ApplicationItem[];

const STAGES: Array<{ key: string; label: string }> = [
  { key: "prospect", label: "Prospect" },
  { key: "applied", label: "Applied" },
  { key: "screen", label: "Screen" },
  { key: "interview", label: "Interview" },
  { key: "offer", label: "Offer" },
  { key: "rejected", label: "Rejected" },
];

export default function ApplicationsPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const applicationsQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["applications", userId],
    queryFn: async () => getJson<ApplicationsResponse>("/applications/", { userId }),
  });

  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: string }) =>
      patchJson(`/applications/${id}`, { stage }, { userId }),
    onSuccess: () => applicationsQuery.refetch(),
  });

  const grouped = STAGES.map(({ key }) => ({ key, items: (applicationsQuery.data ?? []).filter((app) => app.stage === key) }));

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Application Pipeline</h2>
        <p className="mt-2 text-sm text-slate-300">
          Track roles from prospect to offer. Drag-and-drop is coming soon; for now, choose the next stage using the dropdown on each card.
        </p>
      </header>

      {applicationsQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading applications…</p>
      ) : (
        <div className="grid gap-4 overflow-x-auto md:grid-cols-3 xl:grid-cols-6">
          {grouped.map(({ key, items }) => {
            const stageMeta = STAGES.find((stage) => stage.key === key)!;
            return (
              <div key={key} className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/30 p-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-200">{stageMeta.label}</h3>
                  <span className="text-xs text-slate-500">{items.length}</span>
                </div>
                <div className="space-y-3">
                  {items.map((app) => (
                    <article key={app.id} className="space-y-2 rounded-lg border border-slate-800 bg-slate-950/40 p-3">
                      <div>
                        <h4 className="text-sm font-semibold text-slate-200">{app.title || "Untitled"}</h4>
                        <p className="text-xs text-slate-400">{app.company ?? "Unknown company"}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="text-xs text-slate-400">Stage</label>
                        <select
                          value={app.stage}
                          onChange={(event) => stageMutation.mutate({ id: app.id, stage: event.target.value })}
                          className="rounded border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-slate-200"
                        >
                          {STAGES.map((stage) => (
                            <option key={stage.key} value={stage.key}>
                              {stage.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      {app.tasks.length > 0 && (
                        <ul className="space-y-1 text-xs text-slate-400">
                          {app.tasks.map((task) => (
                            <li key={task.id} className="flex items-center gap-2">
                              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
                              <span>{task.title}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                      {app.url && (
                        <a
                          href={app.url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center text-xs text-accent hover:underline"
                        >
                          View posting
                        </a>
                      )}
                    </article>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
