import type { IngestionRun } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableElement, TableHead, TableHeaderCell, TableRow } from "@/components/ui/table";
import { formatDate } from "@/lib/utils/format";

function formatBytes(value: number | null) {
  if (!value) {
    return "stored centrally";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export function ImportHistoryTable({ runs }: { runs: IngestionRun[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Import History</CardTitle>
          <CardDescription>Track import status, duplicates, and row failures before reviewing signal output.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableElement>
            <TableHead>
              <tr>
                <TableHeaderCell>Source</TableHeaderCell>
                <TableHeaderCell>Format</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Rows</TableHeaderCell>
                <TableHeaderCell>Duplicates</TableHeaderCell>
                <TableHeaderCell>Failed</TableHeaderCell>
                <TableHeaderCell>Updated</TableHeaderCell>
              </tr>
            </TableHead>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-ink">{run.source_label}</p>
                      <p className="text-xs text-slate">
                        {run.uploaded_by_email ? `uploaded by ${run.uploaded_by_email}` : "uploaded before hosted auth"}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>{run.import_format.replaceAll("_", " ")}</TableCell>
                  <TableCell>
                    <Badge variant={run.status === "completed" ? "success" : run.status === "failed" ? "danger" : "warning"}>
                      {run.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{run.imported_rows}</TableCell>
                  <TableCell>{run.duplicate_rows}</TableCell>
                  <TableCell>{run.failed_rows}</TableCell>
                  <TableCell>
                    <div>
                      <p>{formatDate(run.updated_at)}</p>
                      <p className="text-xs text-slate">{formatBytes(run.source_file_size_bytes)}</p>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </TableElement>
        </Table>
      </CardContent>
    </Card>
  );
}
