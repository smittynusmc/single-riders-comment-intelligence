import { PageHeader } from "@/components/layout/page-header";
import { MvpPriorityPanel } from "@/components/dashboard/mvp-priority-panel";
import { SignalFilters } from "@/components/signals/signal-filters";
import { SignalCard } from "@/components/signals/signal-card";
import { getAudienceInsights } from "@/lib/api/dashboard";
import { getSignals } from "@/lib/api/signals";

export const dynamic = "force-dynamic";

export default async function SignalsPage() {
  const [response, audienceInsights] = await Promise.all([
    getSignals({ limit: 50 }),
    getAudienceInsights(),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Signals"
        description="Cluster repeated comment themes into ranked MVP signals and compare them against the audience priorities shaping the Single Riders MVP roadmap."
      />
      <MvpPriorityPanel
        title="Audience Priorities Beside The Signal Queue"
        description="Use this ranking to sanity-check whether grouped signals reflect the biggest launch themes from comments and user stories."
        items={audienceInsights.mvp_priorities.slice(0, 3)}
      />
      <SignalFilters />
      <div className="grid gap-6 xl:grid-cols-2">
        {response.items.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </div>
    </div>
  );
}
