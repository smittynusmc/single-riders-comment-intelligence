import { PageHeader } from "@/components/layout/page-header";
import { ClassificationTable } from "@/components/classifications/classification-table";
import { getClassifications } from "@/lib/api/classifications";

export default async function ClassificationsPage() {
  const response = await getClassifications({ limit: 100 });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Classifications"
        description="Review AI output, approve strong calls, override weak ones, and mark false positives before signals drive backlog conversations."
      />
      <ClassificationTable items={response.items} />
    </div>
  );
}
