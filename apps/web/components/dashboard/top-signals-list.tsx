import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardSummary, TopSignalSummary } from "@single-riders/shared-types";
import { formatTitle } from "@/lib/utils/format";

export function TopSignalsList({
  items,
  summary,
}: {
  items: TopSignalSummary[];
  summary: DashboardSummary;
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Top Repeated Requests</CardTitle>
            <CardDescription>Fast read on the signal groups currently pushing backlog priority.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {items.map((item) => (
              <div key={item.id} className="rounded-3xl border border-ink/10 bg-mist/45 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-display text-lg font-semibold text-ink">{item.title}</p>
                    <p className="mt-1 text-sm text-slate">{formatTitle(item.mvp_area)} area</p>
                  </div>
                  <div className="rounded-2xl bg-white px-3 py-2 text-right shadow-sm">
                    <p className="text-xs uppercase tracking-[0.18em] text-slate">Priority</p>
                    <p className="font-display text-xl font-semibold text-coral">{item.priority_score}</p>
                  </div>
                </div>
                <p className="mt-3 text-sm text-slate">Evidence count: {item.evidence_count}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Safety Snapshot</CardTitle>
            <CardDescription>Most common safety and trust issues from classified comments.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {summary.top_safety_concerns.map((item) => (
              <div key={item.key} className="flex items-center justify-between rounded-2xl bg-coral/5 px-4 py-3">
                <span className="text-sm font-medium text-ink">{formatTitle(item.key)}</span>
                <span className="text-sm text-coral">{item.count}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
