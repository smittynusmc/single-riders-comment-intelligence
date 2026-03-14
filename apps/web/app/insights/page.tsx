import { InsightBreakdownGrid } from "@/components/dashboard/insight-breakdown-grid";
import { MvpPriorityPanel } from "@/components/dashboard/mvp-priority-panel";
import { TopVideosList } from "@/components/dashboard/top-videos-list";
import { PageHeader } from "@/components/layout/page-header";
import { getAudienceInsights } from "@/lib/api/dashboard";

export const dynamic = "force-dynamic";

export default async function InsightsPage() {
  const audienceInsights = await getAudienceInsights();

  return (
    <div className="space-y-8">
      <PageHeader
        title="MVP Audience Insights"
        description="Turn TikTok feedback into product decisions by ranking the MVP themes, concerns, and user-story evidence the team should focus on next."
      />
      <MvpPriorityPanel
        title="What Users Care About Most"
        description="Weighted by evidence count, urgency, relevance, confidence, and recent momentum."
        items={audienceInsights.mvp_priorities}
      />
      <InsightBreakdownGrid insights={audienceInsights} />
      <div className="grid gap-6 xl:grid-cols-[1.1fr,1fr]">
        <TopVideosList items={audienceInsights.top_videos} />
        <MvpPriorityPanel
          title="User Story Alignment"
          description="Current feedback mapped to the MVP themes from the Single Riders product docs and beta plan."
          items={audienceInsights.story_alignment}
        />
      </div>
    </div>
  );
}
