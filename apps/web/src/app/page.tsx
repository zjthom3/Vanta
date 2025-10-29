import Link from "next/link";

import { auth } from "@/auth";

const quickLinks = [
  {
    href: "/profile",
    title: "Profile",
    description: "Review and update your headline, summary, and core preferences.",
  },
  {
    href: "/onboarding",
    title: "Complete Onboarding",
    description: "Provide profile basics so agents can personalize daily job scouts.",
  },
  {
    href: "/search-preferences",
    title: "Search Preferences",
    description: "Manage saved searches and daily digest schedules.",
  },
  {
    href: "/feed",
    title: "Job Feed",
    description: "Browse new roles pulled from your connected providers.",
  },
  {
    href: "/health",
    title: "System Health",
    description: "Verify API connectivity and uptime telemetry.",
  },
  {
    href: "https://github.com",
    title: "Repository",
    description: "Review the codebase, workflows, and documentation.",
  },
];

export default async function HomePage() {
  const session = await auth();
  const isAuthenticated = Boolean(session?.user);

  return (
    <section className="space-y-8">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Welcome to Vanta</h2>
        <p className="mt-2 text-sm text-slate-300">
          The orchestrated suite of agents that scouts roles, tailors applications, and keeps
          candidates on track.
        </p>
        {!isAuthenticated && (
          <p className="mt-4 text-sm text-slate-300">
            <Link href="/sign-in" className="underline decoration-dotted underline-offset-4">
              Sign in
            </Link>{" "}
            to get started with onboarding and daily job scouting.
          </p>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {quickLinks
          .filter((link) => isAuthenticated || link.href === "/health" || link.href.startsWith("http"))
          .map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="group rounded-xl border border-slate-800 bg-slate-950/20 p-6 transition hover:border-accent hover:bg-accent-muted"
          >
            <h3 className="text-lg font-medium group-hover:text-accent">{link.title}</h3>
            <p className="mt-2 text-sm text-slate-400">{link.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
