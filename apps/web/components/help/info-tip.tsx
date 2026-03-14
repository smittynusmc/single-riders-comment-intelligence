import { Info } from "lucide-react";

export function InfoTip({
  label,
  description,
}: {
  label: string;
  description: string;
}) {
  return (
    <span className="group relative inline-flex items-center">
      <button
        type="button"
        aria-label={label}
        title={`${label}: ${description}`}
        className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-ink/15 bg-white/85 text-slate transition hover:border-ink/25 hover:text-ink focus:outline-none focus:ring-2 focus:ring-spruce/25"
      >
        <Info className="h-3.5 w-3.5" />
      </button>
      <span className="pointer-events-none absolute left-1/2 top-full z-20 hidden w-64 -translate-x-1/2 rounded-2xl bg-ink px-3 py-2 text-left text-xs leading-5 text-white shadow-panel group-hover:block group-focus-within:block">
        {description}
      </span>
    </span>
  );
}
