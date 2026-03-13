import type { IngestionRun } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableElement, TableHead, TableHeaderCell, TableRow } from "@/components/ui/table";
import { formatDate } from "@/lib/utils/format";

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
                  <TableCell>{run.source_label}</TableCell>
                  <TableCell>
                    <Badge variant={run.status === "completed" ? "success" : run.status === "failed" ? "danger" : "warning"}>
                      {run.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{run.imported_rows}</TableCell>
                  <TableCell>{run.duplicate_rows}</TableCell>
                  <TableCell>{run.failed_rows}</TableCell>
                  <TableCell>{formatDate(run.updated_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </TableElement>
        </Table>
      </CardContent>
    </Card>
  );
}
