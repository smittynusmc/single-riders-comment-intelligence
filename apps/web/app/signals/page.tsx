import { PageHeader } from "@/components/layout/page-header";
import { SignalFilters } from "@/components/signals/signal-filters";
import { SignalCard } from "@/components/signals/signal-card";
import { getSignals } from "@/lib/api/signals";

export default async function SignalsPage() {
  const response = await getSignals({ limit: 50 });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Signals"
        description="Cluster repeated comment themes into ranked MVP signals with evidence, summaries, and export placeholders for backlog handoff."
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
