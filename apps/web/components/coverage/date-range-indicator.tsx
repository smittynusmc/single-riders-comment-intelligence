import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils/format";

export function formatActiveFilterRange(dateFrom?: string, dateTo?: string) {
  if (!dateFrom && !dateTo) {
    return "All imported data";
  }
  if (dateFrom && dateTo) {
    return `${formatDate(dateFrom)} to ${formatDate(dateTo)}`;
  }
  if (dateFrom) {
    return `From ${formatDate(dateFrom)}`;
  }
  return `Through ${formatDate(dateTo)}`;
}

interface DateRangeIndicatorProps {
  earliestCommentDate: string | null;
  latestCommentDate: string | null;
  monthsRepresented: number;
  activeFilterRange: string;
  resultSummary?: string;
}

export function DateRangeIndicator({
  earliestCommentDate,
  latestCommentDate,
  monthsRepresented,
  activeFilterRange,
  resultSummary,
}: DateRangeIndicatorProps) {
  return (
    <Card className="bg-gradient-to-r from-white via-white to-sand/60">
      <CardHeader>
        <div>
          <CardTitle>Date Coverage</CardTitle>
          <CardDescription>See the imported comment span and the currently active date filter at a glance.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 md:grid-cols-4">
          <div className="rounded-3xl bg-paper px-4 py-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate">Earliest</p>
            <p className="mt-2 text-sm font-semibold text-ink">{formatDate(earliestCommentDate)}</p>
          </div>
          <div className="rounded-3xl bg-paper px-4 py-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate">Latest</p>
            <p className="mt-2 text-sm font-semibold text-ink">{formatDate(latestCommentDate)}</p>
          </div>
          <div className="rounded-3xl bg-paper px-4 py-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate">Months Represented</p>
            <p className="mt-2 text-sm font-semibold text-ink">{monthsRepresented}</p>
          </div>
          <div className="rounded-3xl bg-paper px-4 py-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate">Active Filter Range</p>
            <p className="mt-2 text-sm font-semibold text-ink">{activeFilterRange}</p>
          </div>
        </div>
        {resultSummary ? <p className="text-sm text-slate">{resultSummary}</p> : null}
      </CardContent>
    </Card>
  );
}
