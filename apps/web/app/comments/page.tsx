import { CommentFilters } from "@/components/comments/comment-filters";
import { CommentsTable } from "@/components/comments/comments-table";
import { PageHeader } from "@/components/layout/page-header";
import { getComments } from "@/lib/api/comments";

export default async function CommentsPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const params = {
    keyword: typeof searchParams.keyword === "string" ? searchParams.keyword : undefined,
    source_video_id: typeof searchParams.source_video_id === "string" ? searchParams.source_video_id : undefined,
    primary_category: typeof searchParams.primary_category === "string" ? searchParams.primary_category : undefined,
    mvp_area: typeof searchParams.mvp_area === "string" ? searchParams.mvp_area : undefined,
    sentiment: typeof searchParams.sentiment === "string" ? searchParams.sentiment : undefined,
    needs_human_review: typeof searchParams.needs_human_review === "string" ? searchParams.needs_human_review === "true" : undefined,
    date_from: typeof searchParams.date_from === "string" ? searchParams.date_from : undefined,
    date_to: typeof searchParams.date_to === "string" ? searchParams.date_to : undefined,
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
