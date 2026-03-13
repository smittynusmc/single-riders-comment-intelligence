import type { CommentItem, PaginatedResponse } from "@single-riders/shared-types";

import { apiFetch, buildQuery } from "@/lib/api/client";

export function getComments(params: Record<string, string | number | boolean | undefined | null>) {
  return apiFetch<PaginatedResponse<CommentItem>>(`/comments${buildQuery(params)}`);
}
