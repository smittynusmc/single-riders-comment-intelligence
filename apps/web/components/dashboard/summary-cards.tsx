import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardSummary } from "@single-riders/shared-types";

const metrics = (summary: DashboardSummary) => [
  { label: "Total Comments", value: summary.total_comments, tone: "text-ink" },
  { label: "Comments This Week", value: summary.comments_this_week, tone: "text-spruce" },
  { label: "Needs Review", value: summary.needs_review_count, tone: "text-coral" },
  { label: "Active Signals", value: summary.total_signals, tone: "text-gold" },
];

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics(summary).map((metric) => (
        <Card key={metric.label} className="overflow-hidden bg-gradient-to-br from-white to-mist/80">
          <CardHeader>
            <div>
              <CardDescription>{metric.label}</CardDescription>
              <CardTitle className={`mt-2 text-4xl ${metric.tone}`}>{metric.value}</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="text-sm text-slate">
            Signals and review metrics update after each import processing run or manual rebuild.
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
