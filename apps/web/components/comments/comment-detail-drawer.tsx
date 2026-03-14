"use client";

import type { CommentItem } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { formatDate, formatPercent, formatTitle } from "@/lib/utils/format";

export function CommentDetailDrawer({
  comment,
  onOpenChange,
}: {
  comment: CommentItem | null;
  onOpenChange: (open: boolean) => void;
}) {
  const sourceUrl =
    comment && typeof comment.raw_comment.raw_payload_json.url === "string" && comment.raw_comment.raw_payload_json.url
      ? String(comment.raw_comment.raw_payload_json.url)
      : null;

  return (
    <Dialog open={Boolean(comment)} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Comment Detail</DialogTitle>
        <DialogDescription>Inspect the raw comment, normalization, and classification evidence behind this row.</DialogDescription>
        {comment ? (
          <div className="mt-6 space-y-5 text-sm text-ink">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate">Original Comment</p>
              <p className="mt-2 rounded-3xl bg-mist/60 p-4 leading-7">{comment.raw_comment.comment_text}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Video</p>
                <p className="mt-2">{comment.raw_comment.source_video_id ?? "No video id on this export"}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Created</p>
                <p className="mt-2">{formatDate(comment.raw_comment.comment_created_at)}</p>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Author</p>
                <p className="mt-2">{comment.raw_comment.author_handle ?? "Unknown author"}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Source URL</p>
                {sourceUrl ? (
                  <a className="mt-2 inline-block text-sm text-spruce underline underline-offset-4" href={sourceUrl} target="_blank" rel="noreferrer">
                    Open original context
                  </a>
                ) : (
                  <p className="mt-2">No source URL stored in the export</p>
                )}
              </div>
            </div>
            {comment.classification ? (
              <div className="space-y-4 rounded-3xl border border-ink/10 p-4">
                <div className="flex flex-wrap gap-2">
                  <Badge>{formatTitle(comment.classification.primary_category)}</Badge>
                  <Badge variant="success">{formatTitle(comment.classification.mvp_area)}</Badge>
                  <Badge variant={comment.classification.needs_human_review ? "warning" : "default"}>
                    {comment.classification.needs_human_review ? "Needs Review" : "AI Ready"}
                  </Badge>
                </div>
                <p>{comment.classification.rationale_short}</p>
                <p className="text-sm text-slate">{comment.classification.recommended_action}</p>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate">Confidence</p>
                    <p className="mt-2">{formatPercent(comment.classification.confidence)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate">Relevance</p>
                    <p className="mt-2">{formatPercent(comment.classification.mvp_relevance_score)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate">Urgency</p>
                    <p className="mt-2">{formatPercent(comment.classification.urgency_score)}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="rounded-3xl bg-gold/10 p-4 text-gold">Classification has not completed yet for this comment.</p>
            )}
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate">Raw Payload</p>
              <pre className="mt-2 max-h-64 overflow-auto rounded-3xl bg-ink p-4 text-xs leading-6 text-white/85">
                {JSON.stringify(comment.raw_comment.raw_payload_json, null, 2)}
              </pre>
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
