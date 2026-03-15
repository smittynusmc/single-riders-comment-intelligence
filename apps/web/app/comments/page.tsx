import { CommentFilters } from "@/components/comments/comment-filters";
import { CommentsTable } from "@/components/comments/comments-table";
import { DateRangeIndicator, formatActiveFilterRange } from "@/components/coverage/date-range-indicator";
import { DataWarningNotice } from "@/components/feedback/data-warning-notice";
import { ActiveFilterPills, type ActiveFilterPill } from "@/components/filters/active-filter-pills";
import { PageHeader } from "@/components/layout/page-header";
import { getComments } from "@/lib/api/comments";
import { getDashboardSummary } from "@/lib/api/dashboard";

export const dynamic = "force-dynamic";

function buildFilterPills(params: Record<string, string | boolean | number | undefined | null>): ActiveFilterPill[] {
  const pills: ActiveFilterPill[] = [];

  if (params.keyword) {
    pills.push({ key: "keyword", label: "Keyword", value: String(params.keyword) });
  }
  if (params.source_video_id) {
    pills.push({ key: "source_video_id", label: "Source video", value: String(params.source_video_id) });
  }
  if (params.primary_category) {
    pills.push({ key: "primary_category", label: "Category", value: String(params.primary_category).replaceAll("_", " ") });
  }
  if (params.mvp_area) {
    pills.push({ key: "mvp_area", label: "MVP area", value: String(params.mvp_area).replaceAll("_", " ") });
  }
  if (params.sentiment) {
    pills.push({ key: "sentiment", label: "Sentiment", value: String(params.sentiment) });
  }
  if (params.needs_human_review !== undefined) {
    pills.push({
      key: "needs_human_review",
      label: "Review state",
      value: params.needs_human_review ? "needs review" : "no review needed",
    });
  }
  if (params.date_from || params.date_to) {
    pills.push({
      key: "date_range",
      label: "Date",
      value: formatActiveFilterRange(
        typeof params.date_from === "string" ? params.date_from : undefined,
        typeof params.date_to === "string" ? params.date_to : undefined,
      ),
    });
  }

  return pills;
}

export default async function CommentsPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const params = {
    keyword: typeof resolvedSearchParams.keyword === "string" ? resolvedSearchParams.keyword : undefined,
    source_video_id: typeof resolvedSearchParams.source_video_id === "string" ? resolvedSearchParams.source_video_id : undefined,
    primary_category: typeof resolvedSearchParams.primary_category === "string" ? resolvedSearchParams.primary_category : undefined,
    mvp_area: typeof resolvedSearchParams.mvp_area === "string" ? resolvedSearchParams.mvp_area : undefined,
    sentiment: typeof resolvedSearchParams.sentiment === "string" ? resolvedSearchParams.sentiment : undefined,
    needs_human_review:
      typeof resolvedSearchParams.needs_human_review === "string" ? resolvedSearchParams.needs_human_review === "true" : undefined,
    date_from: typeof resolvedSearchParams.date_from === "string" ? resolvedSearchParams.date_from : undefined,
    date_to: typeof resolvedSearchParams.date_to === "string" ? resolvedSearchParams.date_to : undefined,
    limit: 100,
  };

  const [response, summary] = await Promise.all([getComments(params), getDashboardSummary()]);
  const activeFilterRange = formatActiveFilterRange(params.date_from, params.date_to);
  const activeFilterPills = buildFilterPills(params);
  const resultSummary =
    response.meta.total > response.items.length
      ? `Showing ${response.items.length} of ${response.meta.total} comments in the current view.`
      : `${response.meta.total} comments in the current view.`;
  const emptyMessage = activeFilterPills.length
    ? "No comments match the current filters. Older comments may be hidden by the active filters above."
    : "No comments have been imported yet.";

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comments Explorer"
        description="Search imported comments across raw text, normalized output, and AI classification status so the team can inspect evidence behind each emerging product signal."
      />
      <DateRangeIndicator
        earliestCommentDate={summary.earliest_comment_date}
        latestCommentDate={summary.latest_comment_date}
        monthsRepresented={summary.months_represented}
        activeFilterRange={activeFilterRange}
        resultSummary={resultSummary}
      />
      {response.warning ? <DataWarningNotice message={response.warning} /> : null}
      <ActiveFilterPills pills={activeFilterPills} resetHref="/comments" />
      <CommentFilters values={params} />
      <CommentsTable items={response.items} emptyMessage={emptyMessage} />
    </div>
  );
}
