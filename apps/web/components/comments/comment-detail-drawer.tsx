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
                <p className="mt-2">{comment.raw_comment.source_video_id}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate">Created</p>
                <p className="mt-2">{formatDate(comment.raw_comment.comment_created_at)}</p>
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
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
