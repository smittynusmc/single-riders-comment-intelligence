import type { ReactNode } from "react";

import { InfoTip } from "@/components/help/info-tip";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const categoryOptions = [
  "feature_request",
  "bug_or_quality",
  "safety_or_trust",
  "moderation_or_bot",
  "social_coordination",
  "confusion_or_onboarding",
];

const mvpOptions = ["matching", "meetups", "safety", "onboarding", "profiles", "messaging", "moderation", "passholders"];
const sentimentOptions = ["positive", "neutral", "negative", "mixed"];

function FilterField({
  label,
  help,
  children,
}: {
  label: string;
  help: string;
  children: ReactNode;
}) {
  return (
    <label className="space-y-2">
      <span className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate">
        {label}
        <InfoTip label={`${label} help`} description={help} />
      </span>
      {children}
    </label>
  );
}

export function CommentFilters({ values }: { values: Record<string, string | boolean | number | undefined | null> }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <form className="grid gap-4 lg:grid-cols-4" method="get">
          <FilterField label="Keyword" help="Search across raw comment text and normalized text to find specific language or feature requests.">
            <Input name="keyword" placeholder="Keyword" defaultValue={String(values.keyword ?? "")} title="Search comment text for matching words or phrases." />
          </FilterField>
          <FilterField label="Source Video" help="Use this when the export includes a video id and you want feedback from one source post only.">
            <Input name="source_video_id" placeholder="Video ID" defaultValue={String(values.source_video_id ?? "")} title="Filter comments down to one imported source video id." />
          </FilterField>
          <FilterField label="Primary Category" help="Category is the main product interpretation of the comment, such as feature request or safety concern.">
            <select name="primary_category" defaultValue={String(values.primary_category ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink" title="Filter by the AI or reviewer-assigned primary category.">
              <option value="">All categories</option>
              {categoryOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </FilterField>
          <FilterField label="MVP Area" help="MVP area shows which part of the product roadmap the comment most likely affects.">
            <select name="mvp_area" defaultValue={String(values.mvp_area ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink" title="Filter by the product area impacted by the comment.">
              <option value="">All MVP areas</option>
              {mvpOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </FilterField>
          <FilterField label="Sentiment" help="Sentiment tells you whether the tone is positive, neutral, negative, or mixed.">
            <select name="sentiment" defaultValue={String(values.sentiment ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink" title="Filter by the comment's tone.">
              <option value="">All sentiments</option>
              {sentimentOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </FilterField>
          <FilterField label="Review State" help="Use this to isolate comments the AI marked as needing a human decision.">
            <select name="needs_human_review" defaultValue={values.needs_human_review === undefined ? "" : String(values.needs_human_review)} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink" title="Filter by whether a human review is still needed.">
              <option value="">Any review state</option>
              <option value="true">Needs review</option>
              <option value="false">No review needed</option>
            </select>
          </FilterField>
          <FilterField label="From" help="Start date for the comment-created window.">
            <Input name="date_from" type="date" defaultValue={String(values.date_from ?? "")} title="Filter comments created on or after this date." />
          </FilterField>
          <FilterField label="To" help="End date for the comment-created window.">
            <Input name="date_to" type="date" defaultValue={String(values.date_to ?? "")} title="Filter comments created on or before this date." />
          </FilterField>
          <div className="flex items-center gap-3">
            <Button type="submit">Apply Filters</Button>
            <a
              className="inline-flex items-center justify-center rounded-full bg-white px-4 py-2 text-sm font-medium text-ink ring-1 ring-ink/10 transition hover:bg-mist"
              href="/comments"
            >
              Reset
            </a>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
