import { Badge } from "@/components/ui/badge";

export type ActiveFilterPill = {
  key: string;
  label: string;
  value: string;
};

export function ActiveFilterPills({
  pills,
  resetHref,
}: {
  pills: ActiveFilterPill[];
  resetHref: string;
}) {
  if (!pills.length) {
    return (
      <div className="rounded-3xl border border-ink/10 bg-white px-4 py-3 text-sm text-slate">
        No active filters. Showing all imported data.
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-ink/10 bg-white px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs uppercase tracking-[0.18em] text-slate">Active Filters</span>
        {pills.map((pill) => (
          <Badge key={pill.key} variant="default" className="normal-case tracking-normal text-xs">
            {pill.label}: {pill.value}
          </Badge>
        ))}
        <a href={resetHref} className="ml-auto text-sm font-medium text-spruce underline underline-offset-4">
          Clear filters
        </a>
      </div>
    </div>
  );
}
