import { PageHeader } from "@/components/layout/page-header";
import { ImportUploadForm } from "@/components/imports/csv-upload-form";
import { ImportHistoryTable } from "@/components/imports/import-history-table";
import { getImports } from "@/lib/api/imports";

export default async function ImportsPage() {
  const history = await getImports({ limit: 20 });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Imports"
        description="Preview TikTok JSON exports before import, or fall back to CSV for cleaned manual datasets."
      />
      <div className="grid gap-6 xl:grid-cols-[1fr,1.4fr]">
        <ImportUploadForm />
        <ImportHistoryTable runs={history.items} />
      </div>
    </div>
  );
}
