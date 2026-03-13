import type { ReactNode } from "react";
import Link from "next/link";

import { Sidebar } from "@/components/layout/sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-mist bg-grain font-body text-ink">
      <div className="mx-auto flex min-h-screen w-full max-w-[1600px] gap-6 px-4 py-4 lg:px-6">
        <Sidebar />
        <main className="min-w-0 flex-1 rounded-[2rem] border border-white/60 bg-white/65 p-4 shadow-panel backdrop-blur lg:p-6">
          <div className="mb-8 flex items-center justify-between gap-4 rounded-[1.75rem] bg-gradient-to-r from-white via-white to-sand/70 px-5 py-4">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate">Audience Signal Dashboard</p>
              <h1 className="font-display text-2xl font-semibold">Single Riders Comment Intelligence</h1>
            </div>
            <Link href="/imports" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-ink/90">
              Import Comments
            </Link>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
