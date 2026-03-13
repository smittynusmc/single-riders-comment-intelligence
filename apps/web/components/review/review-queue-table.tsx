import { ClassificationTable } from "@/components/classifications/classification-table";
import type { ClassificationReviewItem } from "@single-riders/shared-types";

export function ReviewQueueTable({ items }: { items: ClassificationReviewItem[] }) {
  return <ClassificationTable items={items} />;
}
