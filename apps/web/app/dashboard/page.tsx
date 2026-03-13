import { PageHeader } from "@/components/layout/page-header";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { TopSignalsList } from "@/components/dashboard/top-signals-list";
import { TrendChart } from "@/components/dashboard/trend-chart";
import { getDashboardSummary, getDashboardTrends, getTopSignals } from "@/lib/api/dashboard";

export default async function DashboardPage() {
  const [summary, trends, topSignals] = await Promise.all([
    getDashboardSummary(),
    getDashboardTrends(),
    getTopSignals(),
  ]);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Monitor ingestion volume, AI review pressure, top categories, and the repeated requests shaping the Single Riders MVP backlog."
      />
      <SummaryCards summary={summary} />
      <div className="grid gap-6 xl:grid-cols-[1.5fr,1fr]">
        <TrendChart points={trends} />
        <TopSignalsList items={topSignals} summary={summary} />
      </div>
    </div>
  );
}
