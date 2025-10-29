"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { useState } from "react";

import { deleteRequest, getJson, postJson, putJson } from "@/lib/api-client";

type SearchPref = {
  id: string;
  name: string;
  filters: Record<string, unknown>;
  schedule_cron: string;
  timezone: string;
};

export default function SearchPreferencesPage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;
  const queryClient = useQueryClient();
  const [draftFilters, setDraftFilters] = useState("{}");
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    enabled: Boolean(userId),
    queryKey: ["search-preferences", userId],
    queryFn: async () => getJson<SearchPref[]>("/search-preferences/", { userId }),
  });

  const createMutation = useMutation({
    mutationFn: async (payload: { name: string; filters: Record<string, unknown>; schedule_cron: string; timezone: string }) =>
      postJson<typeof payload, SearchPref>("/search-preferences/", payload, { userId }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["search-preferences", userId] });
      setDraftFilters("{}");
    },
    onError: () => setError("Unable to save search preference. Please try again."),
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Partial<SearchPref> }) =>
      putJson<Partial<SearchPref>, SearchPref>(`/search-preferences/${id}`, payload, { userId }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["search-preferences", userId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteRequest(`/search-preferences/${id}`, { userId }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["search-preferences", userId] });
    },
  });

  const handleCreate = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const form = new FormData(event.currentTarget);
      const parsedFilters = JSON.parse(draftFilters || "{}");
      createMutation.mutate({
        name: form.get("name")?.toString() ?? "",
        filters: parsedFilters,
        schedule_cron: form.get("schedule_cron")?.toString() ?? "0 5 * * *",
        timezone: form.get("timezone")?.toString() ?? "UTC",
      });
    } catch (parseError) {
      setError("Filters must be valid JSON.");
    }
  };

  if (!userId) {
    return (
      <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/40 p-8">
        <h2 className="text-lg font-semibold">Saved searches</h2>
        <p className="text-sm text-slate-300">Sign in to manage your daily job search runs.</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Saved searches</h2>
        <p className="mt-2 text-sm text-slate-300">
          Configure multiple daily digests tuned to different roles, locations, or hybrid preferences.
        </p>
      </div>

      <form
        className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6"
        onSubmit={handleCreate}
      >
        <h3 className="text-sm font-semibold text-slate-200">New search preference</h3>
        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Name</span>
          <input
            required
            name="name"
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
            placeholder="Early-morning roles"
          />
        </label>

        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Filters (JSON)</span>
          <textarea
            name="filters"
            value={draftFilters}
            onChange={(event) => setDraftFilters(event.target.value)}
            rows={3}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-foreground outline-none focus:border-accent"
          />
        </label>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm">
            <span className="text-slate-400">Cron schedule</span>
            <input
              name="schedule_cron"
              defaultValue="0 5 * * *"
              className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
            />
          </label>
          <label className="grid gap-2 text-sm">
            <span className="text-slate-400">Timezone</span>
            <input
              name="timezone"
              defaultValue="UTC"
              className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
            />
          </label>
        </div>

        {error && <p className="text-xs text-rose-400">{error}</p>}

        <button
          type="submit"
          disabled={createMutation.isPending}
          className="w-fit rounded-full bg-accent px-6 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {createMutation.isPending ? "Saving…" : "Save search"}
        </button>
      </form>

      <div className="grid gap-4">
        {isLoading && <p className="text-sm text-slate-400">Loading saved searches…</p>}
        {!isLoading && data && data.length === 0 && (
          <p className="text-sm text-slate-400">No saved searches yet. Create one above to schedule daily runs.</p>
        )}

        {data?.map((pref) => (
          <div key={pref.id} className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/30 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">{pref.name}</h3>
                <p className="text-xs text-slate-400">
                  {pref.schedule_cron} · {pref.timezone}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() =>
                    updateMutation.mutate({ id: pref.id, payload: { schedule_cron: "0 7 * * *" } })
                  }
                  className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-accent"
                >
                  Bump to 7am
                </button>
                <button
                  type="button"
                  onClick={() => deleteMutation.mutate(pref.id)}
                  className="rounded-full border border-rose-800 px-3 py-1 text-xs text-rose-300 transition hover:border-rose-500"
                >
                  Delete
                </button>
              </div>
            </div>
            <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/40 p-3 text-xs text-slate-300">
              {JSON.stringify(pref.filters, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </section>
  );
}
