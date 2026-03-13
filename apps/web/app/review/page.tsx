import { PageHeader } from "@/components/layout/page-header";
import { ReviewQueueTable } from "@/components/review/review-queue-table";
import { getClassifications } from "@/lib/api/classifications";

export default async function ReviewQueuePage() {
  const response = await getClassifications({ needs_human_review: true, limit: 100 });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Human Review Queue"
        description="Handle ambiguous, safety-sensitive, or moderation-related comments that should not flow directly into the backlog without human confirmation."
      />
      <ReviewQueueTable items={response.items} />
    </div>
  );
}
