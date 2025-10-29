import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "System Health • Vanta",
};

async function fetchHealth(): Promise<{ status: string } | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${apiUrl}/health`, { cache: "no-store" });
    if (!res.ok) {
      return null;
    }

    return (await res.json()) as { status: string };
  } catch (error) {
    console.error("Failed to reach API health endpoint", error);
    return null;
  }
}

export default async function HealthPage() {
  const health = await fetchHealth();

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">API Health</h2>
        <p className="mt-2 text-sm text-slate-300">
          A simple ping to the FastAPI service to confirm connectivity.
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-6">
        {health ? (
          <div>
            <span className="text-sm uppercase text-slate-500">Status</span>
            <p className="mt-1 text-2xl font-semibold text-accent">{health.status}</p>
          </div>
        ) : (
          <div>
            <span className="text-sm uppercase text-slate-500">Status</span>
            <p className="mt-1 text-2xl font-semibold text-rose-400">Unavailable</p>
            <p className="mt-2 text-sm text-slate-400">
              Could not reach the API service. Ensure docker-compose services are running or check
              your network settings.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
