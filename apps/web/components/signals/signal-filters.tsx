import { Card, CardContent } from "@/components/ui/card";
import { InfoTip } from "@/components/help/info-tip";

export function SignalFilters() {
  return (
    <Card>
      <CardContent className="flex flex-wrap items-center gap-3 pt-5 text-sm text-slate">
        <span className="inline-flex items-center gap-2 rounded-full bg-ink/5 px-3 py-2">
          Signals are currently ranked by priority score.
          <InfoTip label="Signal ranking help" description="Priority score combines evidence count, relevance, urgency, confidence, and boosts for safety or confusion themes." />
        </span>
        <span className="inline-flex items-center gap-2 rounded-full bg-spruce/10 px-3 py-2 text-spruce">
          Review and export actions update backend state.
          <InfoTip label="Review actions help" description="Mark signals reviewed once the evidence is trustworthy enough to inform roadmap conversations or backlog export." />
        </span>
      </CardContent>
    </Card>
  );
}
