import { CommentFilters } from "@/components/comments/comment-filters";
import { CommentsTable } from "@/components/comments/comments-table";
import { PageHeader } from "@/components/layout/page-header";
import { getComments } from "@/lib/api/comments";

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

  const response = await getComments(params);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comments Explorer"
        description="Search imported comments across raw text, normalized output, and AI classification status so the team can inspect evidence behind each emerging product signal."
      />
      <CommentFilters values={params} />
      <CommentsTable items={response.items} />
    </div>
  );
}
