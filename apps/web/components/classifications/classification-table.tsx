"use client";

import { useTransition } from "react";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import type { ClassificationReviewItem } from "@single-riders/shared-types";

import { updateClassification } from "@/lib/api/classifications";
import { ClassificationBadge } from "@/components/classifications/classification-badge";
import { OverrideModal } from "@/components/classifications/override-modal";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableElement, TableHead, TableHeaderCell, TableRow } from "@/components/ui/table";
import { formatPercent } from "@/lib/utils/format";

const helper = createColumnHelper<ClassificationReviewItem>();

const columns = [
  helper.accessor((row) => row.normalized_comment.original_text, {
    id: "comment",
    header: "Comment",
    cell: (info) => <span className="line-clamp-2 max-w-md">{info.getValue()}</span>,
  }),
  helper.accessor((row) => row.classification.primary_category, {
    id: "category",
    header: "Primary Category",
    cell: (info) => <ClassificationBadge value={info.getValue()} />,
  }),
  helper.accessor((row) => row.classification.mvp_area, {
    id: "mvpArea",
    header: "MVP Area",
    cell: (info) => <ClassificationBadge value={info.getValue()} tone="success" />,
  }),
  helper.accessor((row) => row.classification.sentiment, {
    id: "sentiment",
    header: "Sentiment",
    cell: (info) => <ClassificationBadge value={info.getValue()} tone={info.getValue() === "negative" ? "danger" : "default"} />,
  }),
  helper.accessor((row) => row.classification.confidence, {
    id: "confidence",
    header: "Confidence",
    cell: (info) => formatPercent(info.getValue()),
  }),
  helper.display({
    id: "actions",
    header: "Actions",
    cell: (info) => <ClassificationActions item={info.row.original} />,
  }),
];

function ClassificationActions({ item }: { item: ClassificationReviewItem }) {
  const [isPending, startTransition] = useTransition();

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="primary"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            await updateClassification(item.classification.id, { review_status: "approved" });
            window.location.reload();
          });
        }}
      >
        Approve
      </Button>
      <OverrideModal classificationId={item.classification.id} />
      <Button
        variant="danger"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            await updateClassification(item.classification.id, { is_false_positive: true });
            window.location.reload();
          });
        }}
      >
        False Positive
      </Button>
    </div>
  );
}

export function ClassificationTable({ items }: { items: ClassificationReviewItem[] }) {
  const table = useReactTable({ data: items, columns, getCoreRowModel: getCoreRowModel() });

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>AI Output Review</CardTitle>
          <CardDescription>Approve high-confidence classifications or override anything that should not feed signal grouping as-is.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableElement>
            <TableHead>
              {table.getHeaderGroups().map((group) => (
                <tr key={group.id}>
                  {group.headers.map((header) => (
                    <TableHeaderCell key={header.id}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHeaderCell>
                  ))}
                </tr>
              ))}
            </TableHead>
            <TableBody>
              {table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </TableElement>
        </Table>
      </CardContent>
    </Card>
  );
}
