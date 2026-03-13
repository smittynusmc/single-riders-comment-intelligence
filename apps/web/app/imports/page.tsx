import { PageHeader } from "@/components/layout/page-header";
import { CsvUploadForm } from "@/components/imports/csv-upload-form";
import { ImportHistoryTable } from "@/components/imports/import-history-table";
import { getImports } from "@/lib/api/imports";

export default async function ImportsPage() {
  const history = await getImports({ limit: 20 });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Imports"
        description="Upload TikTok comment CSV exports, watch import outcomes, and confirm duplicate or failure counts before the worker pipeline classifies anything."
      />
      <div className="grid gap-6 xl:grid-cols-[1fr,1.4fr]">
        <CsvUploadForm />
        <ImportHistoryTable runs={history.items} />
      </div>
    </div>
  );
}
