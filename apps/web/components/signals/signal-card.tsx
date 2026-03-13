import type { Signal } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SignalDetailPanel } from "@/components/signals/signal-detail-panel";
import { SignalExportActions } from "@/components/signals/signal-export-actions";
import { formatDate, formatTitle } from "@/lib/utils/format";

export function SignalCard({ signal }: { signal: Signal }) {
  return (
    <Card className="h-full bg-gradient-to-br from-white to-sand/30">
      <CardHeader>
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{formatTitle(signal.primary_category)}</Badge>
            <Badge variant="success">{formatTitle(signal.mvp_area)}</Badge>
            <Badge variant={signal.status === "reviewed" ? "success" : "warning"}>{formatTitle(signal.status)}</Badge>
          </div>
          <div>
            <CardTitle>{signal.title}</CardTitle>
            <CardDescription>{signal.summary}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-3xl bg-white p-4 shadow-sm">
            <p className="text-xs uppercase tracking-[0.18em] text-slate">Priority</p>
            <p className="mt-2 font-display text-3xl text-coral">{signal.priority_score}</p>
          </div>
          <div className="rounded-3xl bg-white p-4 shadow-sm">
            <p className="text-xs uppercase tracking-[0.18em] text-slate">Evidence</p>
            <p className="mt-2 font-display text-3xl text-ink">{signal.evidence_count}</p>
          </div>
          <div className="rounded-3xl bg-white p-4 shadow-sm">
            <p className="text-xs uppercase tracking-[0.18em] text-slate">Last Seen</p>
            <p className="mt-2 text-sm text-ink">{formatDate(signal.last_seen_at)}</p>
          </div>
        </div>
        <SignalDetailPanel signal={signal} />
        <SignalExportActions signal={signal} />
      </CardContent>
    </Card>
  );
}
