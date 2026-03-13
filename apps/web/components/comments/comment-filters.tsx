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

export function CommentFilters({ values }: { values: Record<string, string | boolean | number | undefined | null> }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <form className="grid gap-4 lg:grid-cols-4" method="get">
          <Input name="keyword" placeholder="Keyword" defaultValue={String(values.keyword ?? "")} />
          <Input name="source_video_id" placeholder="Video ID" defaultValue={String(values.source_video_id ?? "")} />
          <select name="primary_category" defaultValue={String(values.primary_category ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink">
            <option value="">All categories</option>
            {categoryOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select name="mvp_area" defaultValue={String(values.mvp_area ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink">
            <option value="">All MVP areas</option>
            {mvpOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select name="sentiment" defaultValue={String(values.sentiment ?? "")} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink">
            <option value="">All sentiments</option>
            {sentimentOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select name="needs_human_review" defaultValue={values.needs_human_review === undefined ? "" : String(values.needs_human_review)} className="h-11 rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink">
            <option value="">Any review state</option>
            <option value="true">Needs review</option>
            <option value="false">No review needed</option>
          </select>
          <Input name="date_from" type="date" defaultValue={String(values.date_from ?? "")} />
          <Input name="date_to" type="date" defaultValue={String(values.date_to ?? "")} />
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
