import type { AudienceInsights } from "@single-riders/shared-types";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function BreakdownCard({
  title,
  description,
  items,
  tone,
}: {
  title: string;
  description: string;
  items: AudienceInsights["mvp_priorities"];
  tone: string;
}) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length ? (
          items.map((item) => (
            <div key={item.key} className="rounded-3xl bg-paper px-4 py-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-ink">{item.label}</p>
                  <p className="mt-1 text-sm text-slate">{item.summary}</p>
                </div>
                <div className={`rounded-full px-3 py-1 text-sm font-semibold ${tone}`}>{item.evidence_count}</div>
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-3xl bg-paper px-4 py-4 text-sm text-slate">No evidence yet.</div>
        )}
      </CardContent>
    </Card>
  );
}

export function InsightBreakdownGrid({ insights }: { insights: AudienceInsights }) {
  return (
    <div className="grid gap-6 xl:grid-cols-3">
      <BreakdownCard
        title="Top User Concerns"
        description="The themes creating trust, launch, or product-risk pressure."
        items={insights.user_concerns}
        tone="bg-coral/10 text-coral"
      />
      <BreakdownCard
        title="Confusion Points"
        description="Areas where onboarding, setup, or expectations are unclear."
        items={insights.confusion_points}
        tone="bg-gold/15 text-gold"
      />
      <BreakdownCard
        title="Positive Validation"
        description="Signals that the product idea resonates and deserves more investment."
        items={insights.positive_validation}
        tone="bg-spruce/10 text-spruce"
      />
    </div>
  );
}
