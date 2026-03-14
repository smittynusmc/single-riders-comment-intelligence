import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { InfoTip } from "@/components/help/info-tip";
import type { DashboardSummary } from "@single-riders/shared-types";

const metrics = (summary: DashboardSummary) => [
  { label: "Total Comments", value: summary.total_comments, tone: "text-ink", help: "All imported comments currently stored in the system." },
  { label: "Comments This Week", value: summary.comments_this_week, tone: "text-spruce", help: "Comments created in the last seven days based on source timestamps when available." },
  { label: "Needs Review", value: summary.needs_review_count, tone: "text-coral", help: "Classifications that still require a human decision before they should influence product calls." },
  { label: "Active Signals", value: summary.total_signals, tone: "text-gold", help: "Grouped product signals currently available for roadmap review and export." },
];

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics(summary).map((metric) => (
        <Card key={metric.label} className="overflow-hidden bg-gradient-to-br from-white to-mist/80">
          <CardHeader>
            <div>
              <CardDescription className="flex items-center gap-2">
                {metric.label}
                <InfoTip label={`${metric.label} help`} description={metric.help} />
              </CardDescription>
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
