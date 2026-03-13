"use client";

import { useState } from "react";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import type { CommentItem } from "@single-riders/shared-types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableElement, TableHead, TableHeaderCell, TableRow } from "@/components/ui/table";
import { CommentDetailDrawer } from "@/components/comments/comment-detail-drawer";
import { formatDate, formatTitle } from "@/lib/utils/format";

const helper = createColumnHelper<CommentItem>();

const columns = [
  helper.accessor((row) => row.raw_comment.comment_created_at ?? row.raw_comment.created_at, {
    id: "date",
    header: "Date",
    cell: (info) => formatDate(info.getValue()),
  }),
  helper.accessor((row) => row.raw_comment.source_video_id, {
    id: "video",
    header: "Video",
  }),
  helper.accessor((row) => row.raw_comment.author_handle ?? "-", {
    id: "handle",
    header: "Handle",
  }),
  helper.accessor((row) => row.raw_comment.comment_text, {
    id: "comment",
    header: "Comment",
    cell: (info) => <span className="line-clamp-2 max-w-md">{info.getValue()}</span>,
  }),
  helper.accessor((row) => row.raw_comment.like_count, {
    id: "likes",
    header: "Likes",
  }),
  helper.accessor((row) => row.normalized_comment?.classification_status ?? "pending", {
    id: "status",
    header: "Classification",
    cell: (info) => <Badge variant={info.getValue() === "needs_review" ? "warning" : "default"}>{formatTitle(info.getValue())}</Badge>,
  }),
];

export function CommentsTable({ items }: { items: CommentItem[] }) {
  const [selected, setSelected] = useState<CommentItem | null>(null);
  const table = useReactTable({ data: items, columns, getCoreRowModel: getCoreRowModel() });

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Comment Inventory</CardTitle>
          <CardDescription>Browse raw imports alongside normalized and classified output.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
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
      </CardContent>
      <CommentDetailDrawer comment={selected} onOpenChange={(open) => !open && setSelected(null)} />
    </Card>
  );
}
