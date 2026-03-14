import type { VideoInsightItem } from "@single-riders/shared-types";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function formatScore(value: number) {
  return value.toFixed(1);
}

export function TopVideosList({ items }: { items: VideoInsightItem[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Top Videos Driving Insight</CardTitle>
          <CardDescription>Where the strongest feedback is showing up, even when portability exports omit video ids.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.length ? (
          items.map((item) => (
            <div key={item.key} className="rounded-[1.75rem] border border-ink/10 bg-gradient-to-r from-white to-mist/60 px-4 py-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium text-ink">{item.label}</p>
                  <p className="mt-1 text-sm text-slate">{item.top_theme ?? "Theme still emerging"}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate">Avg Priority</p>
                  <p className="mt-1 font-display text-2xl text-coral">{formatScore(item.average_priority_score)}</p>
                </div>
              </div>
              <p className="mt-3 text-sm text-slate">{item.comment_count} comments</p>
            </div>
          ))
        ) : (
          <div className="rounded-3xl bg-paper px-4 py-4 text-sm text-slate">Video-level context appears here after imports have been processed.</div>
        )}
      </CardContent>
    </Card>
  );
}
