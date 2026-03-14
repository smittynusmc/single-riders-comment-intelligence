import type { ImportPreview } from "@single-riders/shared-types";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils/format";

export function ImportSummaryCard({ preview }: { preview: ImportPreview }) {
  return (
    <Card className="border border-ink/10 bg-white/85">
      <CardHeader className="pb-3">
        <div>
          <CardTitle>Import Summary</CardTitle>
          <CardDescription>Quick coverage check so you can confirm the file spans the dates you expect before importing.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-4">
        <div className="rounded-3xl bg-paper px-4 py-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate">Total Comments Found</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{preview.comment_count}</p>
        </div>
        <div className="rounded-3xl bg-paper px-4 py-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate">Earliest Comment</p>
          <p className="mt-2 text-sm font-semibold text-ink">{formatDate(preview.earliest_comment_date)}</p>
        </div>
        <div className="rounded-3xl bg-paper px-4 py-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate">Latest Comment</p>
          <p className="mt-2 text-sm font-semibold text-ink">{formatDate(preview.latest_comment_date)}</p>
        </div>
        <div className="rounded-3xl bg-paper px-4 py-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate">Months Represented</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{preview.months_represented || "-"}</p>
        </div>
      </CardContent>
    </Card>
  );
}
