import { DateRangeIndicator } from "@/components/coverage/date-range-indicator";
import { PageHeader } from "@/components/layout/page-header";
import { InsightBreakdownGrid } from "@/components/dashboard/insight-breakdown-grid";
import { MvpPriorityPanel } from "@/components/dashboard/mvp-priority-panel";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { TopSignalsList } from "@/components/dashboard/top-signals-list";
import { TopVideosList } from "@/components/dashboard/top-videos-list";
import { TrendChart } from "@/components/dashboard/trend-chart";
import { getAudienceInsights, getDashboardSummary, getDashboardTrends, getTopSignals } from "@/lib/api/dashboard";

export default async function DashboardPage() {
  const [summary, trends, topSignals, audienceInsights] = await Promise.all([
    getDashboardSummary(),
    getDashboardTrends(),
    getTopSignals(),
    getAudienceInsights(),
  ]);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Monitor what TikTok audiences care about most for the MVP, where confusion is building, and which repeated requests deserve product attention next."
      />
      <DateRangeIndicator
        earliestCommentDate={summary.earliest_comment_date}
        latestCommentDate={summary.latest_comment_date}
        monthsRepresented={summary.months_represented}
        activeFilterRange="All imported data"
      />
      <SummaryCards summary={summary} />
      <MvpPriorityPanel
        title="What Users Care About Most For The MVP"
        description="Ranked audience themes grounded in the Single Riders MVP docs, user stories, and recent comment momentum."
        items={audienceInsights.mvp_priorities}
      />
      <div className="grid gap-6 xl:grid-cols-[1.3fr,1fr]">
        <TrendChart points={trends} />
        <TopSignalsList items={topSignals} summary={summary} />
      </div>
      <InsightBreakdownGrid insights={audienceInsights} />
      <div className="grid gap-6 xl:grid-cols-[1.2fr,1fr]">
        <TopVideosList items={audienceInsights.top_videos} />
        <MvpPriorityPanel
          title="MVP Story Alignment"
          description="How current feedback maps to the product stories driving beta readiness and core launch scope."
          items={audienceInsights.story_alignment.slice(0, 4)}
        />
      </div>
    </div>
  );
}
