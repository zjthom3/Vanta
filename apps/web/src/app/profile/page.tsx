"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { useMemo, useState } from "react";

import { getJson, putJson } from "@/lib/api-client";

type ProfileResponse = {
  id: string;
  headline: string | null;
  summary: string | null;
  skills: string[] | null;
  years_experience: number | null;
  locations: string[] | null;
  work_auth: string | null;
  salary_min_cents: number | null;
  salary_max_cents: number | null;
  remote_only: boolean;
};

export default function ProfilePage() {
  const { data: session } = useSession();
  const userId = session?.user?.id;
  const queryClient = useQueryClient();
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const { data, isLoading, isError } = useQuery({
    enabled: Boolean(userId),
    queryKey: ["profile", userId],
    queryFn: async () => getJson<ProfileResponse>("/profile/me", { userId }),
  });

  const mutation = useMutation({
    mutationFn: async (payload: Partial<ProfileResponse>) =>
      putJson<Partial<ProfileResponse>, ProfileResponse>("/profile/me", payload, { userId }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["profile", userId] });
      setStatusMessage("Profile updated successfully.");
      setTimeout(() => setStatusMessage(null), 4000);
    },
  });

  const skills = useMemo(() => data?.skills?.join(", ") ?? "", [data?.skills]);
  const locations = useMemo(() => data?.locations?.join(", ") ?? "", [data?.locations]);

  if (!userId) {
    return (
      <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/40 p-8">
        <h2 className="text-lg font-semibold">Profile</h2>
        <p className="text-sm text-slate-300">Sign in to review and update your professional profile.</p>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8">
        <p className="text-sm text-slate-400">Loading profile…</p>
      </section>
    );
  }

  if (isError || !data) {
    return (
      <section className="rounded-2xl border border-rose-900/30 bg-rose-500/10 p-8">
        <p className="text-sm text-rose-200">We couldn&apos;t load your profile. Please try again later.</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Professional profile</h2>
        <p className="mt-2 text-sm text-slate-300">
          Keep your headline, elevator pitch, and search preferences up to date. We use this
          information to personalize job scouting and resume tailoring.
        </p>
      </div>

      <form
        className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6"
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          const payload = {
            headline: form.get("headline")?.toString().trim() || null,
            summary: form.get("summary")?.toString().trim() || null,
            skills: form
              .get("skills")
              ?.toString()
              .split(",")
              .map((value) => value.trim())
              .filter(Boolean) ?? [],
            locations: form
              .get("locations")
              ?.toString()
              .split(",")
              .map((value) => value.trim())
              .filter(Boolean) ?? [],
            remote_only: form.get("remote_only") === "on",
            work_auth: form.get("work_auth")?.toString().trim() || null,
          };

          mutation.mutate(payload);
        }}
      >
        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Headline</span>
          <input
            type="text"
            name="headline"
            defaultValue={data.headline ?? ""}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
          />
        </label>

        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Summary</span>
          <textarea
            name="summary"
            defaultValue={data.summary ?? ""}
            rows={4}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-foreground outline-none focus:border-accent"
          />
        </label>

        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Skills (comma separated)</span>
          <input
            type="text"
            name="skills"
            defaultValue={skills}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
          />
        </label>

        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Preferred locations (comma separated)</span>
          <input
            type="text"
            name="locations"
            defaultValue={locations}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
          />
        </label>

        <label className="grid gap-2 text-sm">
          <span className="text-slate-400">Work authorization</span>
          <input
            type="text"
            name="work_auth"
            defaultValue={data.work_auth ?? ""}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
          />
        </label>

        <label className="flex items-center gap-2 text-sm text-slate-200">
          <input type="checkbox" name="remote_only" defaultChecked={data.remote_only} />
          Open to remote-only roles
        </label>

        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-full bg-accent px-6 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
          >
            {mutation.isPending ? "Saving…" : "Save profile"}
          </button>

          {statusMessage && <span className="text-xs text-emerald-300">{statusMessage}</span>}
        </div>
      </form>
    </section>
  );
}
