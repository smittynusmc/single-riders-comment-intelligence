import Link from "next/link";

import { cn } from "@/lib/utils/cn";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/imports", label: "Imports" },
  { href: "/comments", label: "Comments" },
  { href: "/classifications", label: "Classifications" },
  { href: "/signals", label: "Signals" },
  { href: "/review", label: "Review Queue" },
];

export function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 rounded-[2rem] bg-ink p-6 text-white shadow-panel lg:block">
      <div className="mb-10">
        <p className="text-xs uppercase tracking-[0.3em] text-white/60">Internal Tool</p>
        <h2 className="mt-3 font-display text-2xl font-semibold">Feedback Signal Engine</h2>
        <p className="mt-3 text-sm leading-6 text-white/70">
          CSV-first social comment intelligence for backlog planning, review workflows, and export handoff.
        </p>
      </div>
      <nav className="space-y-2">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "block rounded-2xl px-4 py-3 text-sm font-medium text-white/75 transition hover:bg-white/10 hover:text-white",
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-white/50">Phase 1</p>
        <p className="mt-2 text-sm leading-6 text-white/75">
          CSV import is the MVP ingestion path. Manual and third-party adapters can plug into the same backend contract later.
        </p>
      </div>
    </aside>
  );
}
