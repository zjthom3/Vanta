"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";

import { getJson, postFormData } from "@/lib/api-client";
import { useOnboardingStore, type OnboardingFormState } from "@/store/onboarding";

const roleOptions = ["Product Manager", "Customer Success Manager", "Software Engineer"];
const locationOptions = ["Remote", "San Francisco", "New York", "Toronto", "London"];
const timezoneOptions = ["UTC", "America/New_York", "America/Los_Angeles", "America/Toronto", "Europe/London"];
const dailyCronOptions: Array<{ label: string; value: string }> = [
  { label: "Daily at 5:00 AM", value: "0 5 * * *" },
  { label: "Daily at 6:00 AM", value: "0 6 * * *" },
  { label: "Daily at 7:00 AM", value: "0 7 * * *" },
];

interface OnboardingResponse {
  next_step: string;
  message: string;
  resume_version_id?: string | null;
  resume_doc_url?: string | null;
}

interface ResumePreview {
  id: string;
  original_filename: string | null;
  content_type: string | null;
  sections: Record<string, unknown> | null;
  keywords: string[] | null;
  ats_score: number | null;
}

const steps = ["Basics", "Preferences", "Resume", "Review"] as const;

export default function OnboardingPage() {
  const state = useOnboardingStore();
  const updateField = useOnboardingStore((store) => store.updateField);
  const reset = useOnboardingStore((store) => store.reset);
  const [stepIndex, setStepIndex] = useState(0);
  const [validationAttempts, setValidationAttempts] = useState({ basics: false, preferences: false });
  const [submissionComplete, setSubmissionComplete] = useState(false);
  const [submittedSnapshot, setSubmittedSnapshot] = useState<OnboardingFormState | null>(null);
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const mutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData();
      formData.append("full_name", state.fullName);
      formData.append("email", state.email);
      formData.append("primary_role", state.primaryRole);
      state.targetLocations.forEach((location) => formData.append("target_locations", location));
      formData.append("years_experience", String(state.yearsExperience));
      formData.append("schedule_cron", state.scheduleCron);
      formData.append("timezone", state.timezone);

      if (state.resumeFile) {
        formData.append("resume", state.resumeFile, state.resumeFile.name);
      }

      return postFormData<OnboardingResponse>("/onboarding/profile", formData, { userId });
    },
    onSuccess: () => {
      setValidationAttempts({ basics: false, preferences: false });
      setSubmissionComplete(true);
      setStepIndex(steps.length - 1);
      reset();
    },
  });

  const resumePreview = useQuery({
    queryKey: ["resume-preview", mutation.data?.resume_version_id],
    enabled: Boolean(mutation.data?.resume_version_id && userId),
    queryFn: async () => getJson<ResumePreview>(`/resumes/${mutation.data?.resume_version_id}`, { userId }),
    staleTime: 60_000,
  });

  useEffect(() => {
    if (stepIndex < steps.length - 1 && submissionComplete) {
      setSubmissionComplete(false);
      mutation.reset();
    }
  }, [stepIndex, submissionComplete, mutation]);

  const canProceedBasics = useMemo(() => {
    return state.fullName.trim().length > 0 && state.email.trim().length > 0;
  }, [state.fullName, state.email]);

  const canProceedPreferences = useMemo(() => {
    return (
      state.primaryRole.trim().length > 0 &&
      state.targetLocations.length > 0 &&
      state.scheduleCron.trim().length > 0 &&
      state.timezone.trim().length > 0
    );
  }, [state.primaryRole, state.targetLocations, state.scheduleCron, state.timezone]);

  const showSubmit = stepIndex === steps.length - 1;

  const resumeSections = (resumePreview.data?.sections ?? undefined) as Record<string, unknown> | undefined;
  const resumeSummary =
    resumeSections && typeof resumeSections["summary"] === "string" ? (resumeSections["summary"] as string) : null;
  const resumeExperience =
    resumeSections && Array.isArray(resumeSections["experience"])
      ? (resumeSections["experience"] as string[])
      : null;

  const handleNext = () => {
    if (!userId) {
      return;
    }
    if (stepIndex === 0 && !canProceedBasics) {
      setValidationAttempts((prev) => ({ ...prev, basics: true }));
      return;
    }
    if (stepIndex === 1 && !canProceedPreferences) {
      setValidationAttempts((prev) => ({ ...prev, preferences: true }));
      return;
    }
    setStepIndex((current) => Math.min(current + 1, steps.length - 1));
  };

  const handleBack = () => {
    if (stepIndex === steps.length - 1) {
      mutation.reset();
      setSubmissionComplete(false);
    }
    setStepIndex((current) => Math.max(current - 1, 0));
  };

  const onToggleLocation = (location: string) => {
    const next = state.targetLocations.includes(location)
      ? state.targetLocations.filter((value) => value !== location)
      : [...state.targetLocations, location];
    updateField("targetLocations", next);
  };

  const handleSubmit = () => {
    if (!userId) {
      return;
    }
    if (!canProceedBasics || !canProceedPreferences) {
      setValidationAttempts({ basics: true, preferences: true });
      return;
    }
    const snapshot: OnboardingFormState = {
      ...state,
      targetLocations: [...state.targetLocations],
      resumeFile: state.resumeFile,
    };
    setSubmittedSnapshot(snapshot);
    setSubmissionComplete(false);
    mutation.mutate();
  };

  const activeSummary = submittedSnapshot ?? state;

  return (
    <section className="space-y-8">
      {!userId && (
        <div className="rounded-xl border border-amber-700/40 bg-amber-500/10 p-4 text-sm text-amber-200">
          Please sign in to complete onboarding and personalize your job search.
        </div>
      )}
      <div className="space-y-8">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
          <h2 className="text-xl font-semibold">Get set up in four quick steps</h2>
          <p className="mt-2 text-sm text-slate-300">
            Share your basics, tune preferences, upload a resume, and review everything before submitting.
          </p>
          <div className="mt-6 flex items-center gap-4 text-xs uppercase tracking-wide text-slate-500">
            {steps.map((label, index) => (
              <div key={label} className="flex items-center gap-2">
                <div
                  className={`flex h-6 w-6 items-center justify-center rounded-full border text-[11px] ${
                    index === stepIndex
                      ? "border-accent bg-accent text-slate-950"
                      : index < stepIndex
                        ? "border-emerald-500 bg-emerald-500/10 text-emerald-400"
                        : "border-slate-700 text-slate-500"
                  }`}
                >
                  {index + 1}
                </div>
                <span>{label}</span>
                {index < steps.length - 1 && <div className="h-px w-10 bg-slate-700" />}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          {stepIndex === 0 && (
            <section className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6">
              <h3 className="text-sm font-semibold text-slate-200">Basics</h3>
              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Full name</span>
                <input
                  required
                  value={state.fullName}
                  onChange={(event) => updateField("fullName", event.target.value)}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                  placeholder="Ada Lovelace"
                  type="text"
                />
              </label>
              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Email</span>
                <input
                  required
                  value={state.email}
                  onChange={(event) => updateField("email", event.target.value)}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                  placeholder="you@example.com"
                  type="email"
                />
              </label>
              {validationAttempts.basics && !canProceedBasics && (
                <p className="text-xs text-rose-400">Please add both your full name and a valid email to continue.</p>
              )}
            </section>
          )}

          {stepIndex === 1 && (
            <section className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6">
              <h3 className="text-sm font-semibold text-slate-200">Preferences</h3>
              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Primary role</span>
                <select
                  value={state.primaryRole}
                  onChange={(event) => updateField("primaryRole", event.target.value)}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                >
                  <option value="" disabled>
                    Select a role
                  </option>
                  {roleOptions.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </label>

              <div className="grid gap-2 text-sm">
                <span className="text-slate-400">Target locations</span>
                <div className="flex flex-wrap gap-2">
                  {locationOptions.map((location) => {
                    const active = state.targetLocations.includes(location);
                    return (
                      <button
                        key={location}
                        type="button"
                        onClick={() => onToggleLocation(location)}
                        className={`rounded-full border px-4 py-1 text-xs font-medium transition ${
                          active
                            ? "border-accent bg-accent/10 text-accent"
                            : "border-slate-800 bg-slate-950 text-slate-300 hover:border-accent"
                        }`}
                      >
                        {location}
                      </button>
                    );
                  })}
                </div>
              </div>

              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Years of experience</span>
                <input
                  type="number"
                  min={0}
                  max={60}
                  value={state.yearsExperience}
                  onChange={(event) => updateField("yearsExperience", Number(event.target.value))}
                  className="w-24 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                />
              </label>

              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Daily digest time</span>
                <select
                  value={state.scheduleCron}
                  onChange={(event) => updateField("scheduleCron", event.target.value)}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                >
                  {dailyCronOptions.map(({ label, value }) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid gap-2 text-sm">
                <span className="text-slate-400">Timezone</span>
                <select
                  value={state.timezone}
                  onChange={(event) => updateField("timezone", event.target.value)}
                  className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-base text-foreground outline-none focus:border-accent"
                >
                  {timezoneOptions.map((tz) => (
                    <option key={tz} value={tz}>
                      {tz}
                    </option>
                  ))}
                </select>
              </label>

              {validationAttempts.preferences && !canProceedPreferences && (
                <p className="text-xs text-rose-400">Choose at least one target location and a primary role to proceed.</p>
              )}
            </section>
          )}

          {stepIndex === 2 && (
            <section className="grid gap-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6">
              <h3 className="text-sm font-semibold text-slate-200">Resume (optional)</h3>
              <label className="flex h-32 cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700 bg-slate-950/40 text-sm text-slate-400 hover:border-accent">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0] ?? null;
                    updateField("resumeFile", file ?? null);
                  }}
                />
                {state.resumeFile ? (
                  <span className="text-slate-200">{state.resumeFile.name}</span>
                ) : (
                  <>
                    <span>Upload your resume (PDF or DOCX)</span>
                    <span className="text-xs text-slate-500">Optional — we&apos;ll parse and pre-fill your experience instantly.</span>
                  </>
                )}
              </label>

              <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-sm text-slate-300">
                <p className="font-medium text-slate-200">Summary</p>
                <ul className="mt-2 space-y-1 text-xs text-slate-400">
                  <li>{state.fullName || "Your full name"}</li>
                  <li>{state.email || "Email"}</li>
                  <li>{state.primaryRole || "Primary role"}</li>
                  <li>{state.targetLocations.length > 0 ? state.targetLocations.join(", ") : "Preferred locations"}</li>
                  <li>
                    Daily digest: {dailyCronOptions.find((opt) => opt.value === state.scheduleCron)?.label ?? state.scheduleCron}
                  </li>
                  <li>Timezone: {state.timezone}</li>
                </ul>
              </div>
            </section>
          )}

          {stepIndex === 3 && (
            <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-950/30 p-6">
              <h3 className="text-sm font-semibold text-slate-200">Review &amp; submit</h3>
              <div className="grid gap-2 text-sm">
                <span className="text-slate-400">Overview</span>
                <ul className="space-y-1 text-xs text-slate-300">
                  <li>Name: {activeSummary.fullName}</li>
                  <li>Email: {activeSummary.email}</li>
                  <li>Primary role: {activeSummary.primaryRole || "—"}</li>
                  <li>
                    Locations: {activeSummary.targetLocations.length ? activeSummary.targetLocations.join(", ") : "—"}
                  </li>
                  <li>Experience: {activeSummary.yearsExperience} years</li>
                  <li>
                    Daily digest: {dailyCronOptions.find((opt) => opt.value === activeSummary.scheduleCron)?.label ?? activeSummary.scheduleCron}
                  </li>
                  <li>Timezone: {activeSummary.timezone}</li>
                </ul>
              </div>

              {mutation.isSuccess && (
                <div className="rounded-lg border border-emerald-700/40 bg-emerald-500/10 p-4 text-sm text-emerald-300">
                  <p>{mutation.data?.message}</p>
                  {mutation.data?.resume_doc_url && (
                    <p className="mt-1 text-xs text-emerald-200">
                      Resume stored at <span className="underline">{mutation.data.resume_doc_url}</span>
                    </p>
                  )}
                </div>
              )}

              {mutation.data?.resume_version_id && (
                <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300">Parsed resume preview</span>
                    <span className="text-xs text-slate-500">
                      {resumePreview.isFetching ? "Loading..." : submissionComplete ? "Ready" : "Pending"}
                    </span>
                  </div>
                  {resumeSections && Object.keys(resumeSections).length > 0 ? (
                    <div className="mt-3 space-y-2 text-xs text-slate-400">
                      {resumeSummary && (
                        <p>
                          <span className="font-semibold text-slate-300">Summary:</span> {resumeSummary}
                        </p>
                      )}
                      {resumeExperience && (
                        <div>
                          <p className="font-semibold text-slate-300">Experience Highlights</p>
                          <ul className="mt-1 list-disc space-y-1 pl-4">
                            {resumeExperience.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="mt-3 text-xs text-slate-500">
                      {resumePreview.isFetching
                        ? "Parsing your resume..."
                        : "No parsed content yet. We'll continue processing in the background."}
                    </p>
                  )}
                  {resumePreview.data?.keywords?.length ? (
                    <p className="mt-3 text-xs text-slate-400">
                      <span className="font-semibold text-slate-300">Keywords:</span> {resumePreview.data.keywords.join(", ")}
                    </p>
                  ) : null}
                  {typeof resumePreview.data?.ats_score === "number" && (
                    <p className="mt-1 text-xs text-slate-400">
                      <span className="font-semibold text-slate-300">ATS score:</span> {resumePreview.data.ats_score}
                    </p>
                  )}
                </div>
              )}
            </section>
          )}

          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={handleBack}
              disabled={stepIndex === 0 || mutation.isPending}
              className="rounded-full border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-accent disabled:cursor-not-allowed disabled:opacity-50"
            >
              Back
            </button>

            {!showSubmit && (
              <button
                type="button"
                onClick={handleNext}
                disabled={
                  mutation.isPending ||
                  (stepIndex === 0 && !canProceedBasics) ||
                  (stepIndex === 1 && !canProceedPreferences)
                }
                className="rounded-full bg-accent px-6 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              >
                Next
              </button>
            )}

            {showSubmit && (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={
                  mutation.isPending ||
                  !userId ||
                  !canProceedBasics ||
                  !canProceedPreferences
                }
                className="rounded-full bg-accent px-6 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              >
                {mutation.isPending ? "Submitting..." : submissionComplete ? "Submitted" : "Finish"}
              </button>
            )}
          </div>

          {mutation.isError && (
            <p className="text-sm text-rose-400">
              {(mutation.error as Error)?.message ?? "Unable to save profile. Please try again."}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
