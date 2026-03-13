import type { Signal } from "@single-riders/shared-types";

export function SignalDetailPanel({ signal }: { signal: Signal }) {
  return (
    <div className="space-y-4 rounded-3xl border border-ink/10 bg-white/80 p-4">
      <div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate">Suggested Backlog Action</p>
        <p className="mt-2 text-sm leading-6 text-ink">{signal.suggested_backlog_action}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate">Sample Comments</p>
        <div className="mt-3 space-y-2">
          {signal.sample_comments.map((sample, index) => (
            <div key={`${signal.id}-${index}`} className="rounded-2xl bg-mist/70 p-3 text-sm text-ink">
              {String(sample.text ?? sample.comment_text ?? "No sample text available")}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
