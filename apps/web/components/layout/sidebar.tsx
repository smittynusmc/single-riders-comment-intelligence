import Link from "next/link";

import { InfoTip } from "@/components/help/info-tip";
import { cn } from "@/lib/utils/cn";

const items = [
  { href: "/dashboard", label: "Dashboard", description: "High-level read on comment volume, review pressure, and the biggest audience themes." },
  { href: "/insights", label: "Audience Insights", description: "Ranks what users care about most for the MVP using grouped evidence, momentum, and story alignment." },
  { href: "/imports", label: "Imports", description: "Preview TikTok exports, confirm scope, and import approved comment data into the pipeline." },
  { href: "/comments", label: "Comments", description: "Explore raw evidence, classifications, and audit details behind each imported comment." },
  { href: "/classifications", label: "Classifications", description: "Inspect AI decisions, approve strong calls, and override weak or incorrect labels." },
  { href: "/signals", label: "Signals", description: "Review grouped MVP themes and prepare backlog-ready signal summaries." },
  { href: "/review", label: "Review Queue", description: "Handle ambiguous, safety-sensitive, or low-confidence comments that need human input." },
  { href: "/guide", label: "Guide", description: "Step-by-step help, glossary notes, and workflow guidance for using the app well." },
] as const;

export function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 rounded-[2rem] bg-ink p-6 text-white shadow-panel lg:block">
      <div className="mb-10">
        <p className="text-xs uppercase tracking-[0.3em] text-white/60">Internal Tool</p>
        <h2 className="mt-3 font-display text-2xl font-semibold">Feedback Signal Engine</h2>
        <p className="mt-3 text-sm leading-6 text-white/70">
          JSON-first social comment intelligence for backlog planning, review workflows, and export handoff.
        </p>
      </div>
      <nav className="space-y-2">
        {items.map((item) => (
          <div key={item.href} className="flex items-center gap-2">
            <Link
              href={item.href}
              title={item.description}
              className={cn(
                "block flex-1 rounded-2xl px-4 py-3 text-sm font-medium text-white/75 transition hover:bg-white/10 hover:text-white",
              )}
            >
              {item.label}
            </Link>
            <InfoTip label={`${item.label} help`} description={item.description} />
          </div>
        ))}
      </nav>
      <div className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-white/50">Phase 1</p>
        <p className="mt-2 text-sm leading-6 text-white/75">
          TikTok JSON export upload is the MVP ingestion path. CSV, manual paste, and approved connectors can plug into the same contract later.
        </p>
      </div>
    </aside>
  );
}
