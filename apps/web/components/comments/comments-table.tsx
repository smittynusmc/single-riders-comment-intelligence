"use client";

import { useState } from "react";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import type { CommentItem } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { ClassificationBadge } from "@/components/classifications/classification-badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableElement, TableHead, TableHeaderCell, TableRow } from "@/components/ui/table";
import { CommentDetailDrawer } from "@/components/comments/comment-detail-drawer";
import { formatDate, formatTitle } from "@/lib/utils/format";

const helper = createColumnHelper<CommentItem>();

function effectiveCategory(item: CommentItem) {
  return item.classification?.override_primary_category ?? item.classification?.primary_category ?? null;
}

function effectiveMvpArea(item: CommentItem) {
  return item.classification?.override_mvp_area ?? item.classification?.mvp_area ?? null;
}

function priorityScore(item: CommentItem) {
  if (!item.classification) {
    return "-";
  }

  const score =
    (item.classification.mvp_relevance_score * 0.45) +
    (item.classification.urgency_score * 0.35) +
    (item.classification.confidence * 0.2);
  return `${Math.round(score * 100)}`;
}

const columns = [
  helper.accessor((row) => row.raw_comment.comment_created_at ?? row.raw_comment.created_at, {
    id: "date",
    header: "Date",
    cell: (info) => formatDate(info.getValue()),
  }),
  helper.accessor((row) => row.raw_comment.source_video_id ?? String(row.raw_comment.raw_payload_json.url ?? "Portability export"), {
    id: "source",
    header: "Source",
    cell: (info) => <span className="line-clamp-1 max-w-44 text-sm text-slate">{info.getValue()}</span>,
  }),
  helper.accessor((row) => row.raw_comment.comment_text, {
    id: "comment",
    header: "Comment",
    cell: (info) => <span className="line-clamp-2 max-w-md">{info.getValue()}</span>,
  }),
  helper.accessor((row) => effectiveCategory(row), {
    id: "category",
    header: "Category",
    cell: (info) => {
      const value = info.getValue();
      return value ? <ClassificationBadge value={value} /> : <span className="text-slate">Pending</span>;
    },
  }),
  helper.accessor((row) => row.classification?.sentiment ?? null, {
    id: "sentiment",
    header: "Sentiment",
    cell: (info) => {
      const value = info.getValue();
      return value ? (
        <ClassificationBadge value={value} tone={value === "negative" ? "danger" : "default"} />
      ) : (
        <span className="text-slate">Pending</span>
      );
    },
  }),
  helper.accessor((row) => effectiveMvpArea(row), {
    id: "mvpArea",
    header: "MVP Area",
    cell: (info) => {
      const value = info.getValue();
      return value ? <ClassificationBadge value={value} tone="success" /> : <span className="text-slate">Pending</span>;
    },
  }),
  helper.accessor((row) => priorityScore(row), {
    id: "priority",
    header: "Priority",
  }),
  helper.accessor((row) => row.classification?.review_status ?? row.normalized_comment?.classification_status ?? "pending", {
    id: "status",
    header: "Review Status",
    cell: (info) => (
      <Badge
        variant={
          info.getValue() === "needs_review"
            ? "warning"
            : info.getValue() === "approved"
              ? "success"
              : info.getValue() === "false_positive"
                ? "danger"
                : "default"
        }
      >
        {formatTitle(info.getValue())}
      </Badge>
    ),
  }),
];

export function CommentsTable({
  items,
  emptyMessage,
}: {
  items: CommentItem[];
  emptyMessage?: string;
}) {
  const [selected, setSelected] = useState<CommentItem | null>(null);
  const table = useReactTable({ data: items, columns, getCoreRowModel: getCoreRowModel() });

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Comment Inventory</CardTitle>
          <CardDescription>Browse the evidence behind MVP themes, concerns, and classifications without leaving the explorer.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        {items.length ? (
          <Table>
            <TableElement>
              <TableHead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHeaderCell key={header.id}>
                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                      </TableHeaderCell>
                    ))}
                  </tr>
                ))}
              </TableHead>
              <TableBody>
                {table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id} className="cursor-pointer" onClick={() => setSelected(row.original)}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </TableElement>
          </Table>
        ) : (
          <div className="rounded-3xl border border-dashed border-ink/15 bg-paper px-5 py-8 text-sm leading-6 text-slate">
            {emptyMessage ?? "No comments are available in this view yet."}
          </div>
        )}
      </CardContent>
      <CommentDetailDrawer comment={selected} onOpenChange={(open) => !open && setSelected(null)} />
    </Card>
  );
}
