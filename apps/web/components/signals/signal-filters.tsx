import { Card, CardContent } from "@/components/ui/card";

export function SignalFilters() {
  return (
    <Card>
      <CardContent className="flex flex-wrap items-center gap-3 pt-5 text-sm text-slate">
        <span className="rounded-full bg-ink/5 px-3 py-2">Signals are currently ranked by priority score.</span>
        <span className="rounded-full bg-spruce/10 px-3 py-2 text-spruce">Review and export actions update backend state.</span>
      </CardContent>
    </Card>
  );
}
