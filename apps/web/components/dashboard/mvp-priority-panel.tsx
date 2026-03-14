import type { AudienceThemeInsight } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatTitle } from "@/lib/utils/format";

function formatScore(value: number) {
  return value.toFixed(1);
}

export function MvpPriorityPanel({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: AudienceThemeInsight[];
}) {
  return (
    <Card className="overflow-hidden bg-gradient-to-br from-white via-white to-sand/55">
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.length ? (
          items.map((item, index) => (
            <div
              key={item.key}
              className="rounded-[1.75rem] border border-ink/10 bg-white/90 p-4 shadow-sm transition hover:-translate-y-0.5"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-ink px-3 py-1 text-xs uppercase tracking-[0.18em] text-white/85">
                      #{index + 1}
                    </span>
                    {item.mvp_area ? <Badge variant="success">{formatTitle(item.mvp_area)}</Badge> : null}
                    {item.primary_category ? <Badge>{formatTitle(item.primary_category)}</Badge> : null}
                    <Badge variant={item.trend_label === "Rising" ? "warning" : "default"}>{item.trend_label}</Badge>
                  </div>
                  <div>
                    <h3 className="font-display text-xl font-semibold text-ink">{item.label}</h3>
                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate">{item.summary}</p>
                  </div>
                </div>
                <div className="min-w-32 rounded-[1.5rem] bg-mist/70 px-4 py-3 text-right">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">Priority</p>
                  <p className="mt-2 font-display text-3xl text-coral">{formatScore(item.weighted_score)}</p>
                </div>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-paper px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">Evidence</p>
                  <p className="mt-1 text-sm font-semibold text-ink">{item.evidence_count} comments</p>
                </div>
                <div className="rounded-2xl bg-paper px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">Recent Momentum</p>
                  <p className="mt-1 text-sm font-semibold text-ink">
                    {item.recent_evidence_count} recent · {formatScore(item.momentum)}%
                  </p>
                </div>
                <div className="rounded-2xl bg-paper px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">User Story Fit</p>
                  <p className="mt-1 text-sm font-medium leading-6 text-ink">{item.story_anchor}</p>
                </div>
              </div>
              {item.sample_comments.length ? (
                <div className="mt-4 space-y-2">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">Representative Comments</p>
                  <div className="grid gap-2 lg:grid-cols-3">
                    {item.sample_comments.map((sample) => (
                      <div key={`${item.key}-${sample}`} className="rounded-2xl bg-sand/45 px-4 py-3 text-sm leading-6 text-ink">
                        {sample}
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          ))
        ) : (
          <div className="rounded-3xl bg-paper px-5 py-4 text-sm text-slate">
            No ranked audience themes yet. Import comments and run the processing pipeline to populate this view.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
