import "./globals.css";
import type { Metadata } from "next";

import { Providers } from "./providers";
import { UserNav } from "@/components/user-nav";

export const metadata: Metadata = {
  title: "Vanta",
  description: "AI-powered job search copilot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-background">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <Providers>
          <main className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-6 py-12">
            <header className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">Vanta</h1>
                <p className="text-sm text-slate-400">
                  Automate every step of the job-hunting process with trusted AI agents.
                </p>
              </div>
              <UserNav />
            </header>
            <div className="flex-1">{children}</div>
            <footer className="border-t border-slate-800 pt-6 text-xs text-slate-500">
              © {new Date().getFullYear()} Vanta. All rights reserved.
            </footer>
          </main>
        </Providers>
      </body>
    </html>
  );
}
