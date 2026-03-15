import type { CommentItem, PaginatedResponse } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch, buildQuery } from "@/lib/api/client";
import { buildUnavailablePaginatedResponse, type FallbackPaginatedResponse } from "@/lib/api/fallback";

export function getComments(
  params: Record<string, string | number | boolean | undefined | null>,
): Promise<FallbackPaginatedResponse<CommentItem>> {
  const limit = typeof params.limit === "number" ? params.limit : 50;
  const offset = typeof params.offset === "number" ? params.offset : 0;

  return apiFetch<PaginatedResponse<CommentItem>>(`/comments${buildQuery(params)}`).catch((error): FallbackPaginatedResponse<CommentItem> => {
    if (error instanceof ApiRequestError && error.status === 404) {
      return buildUnavailablePaginatedResponse(
        "Comments are temporarily unavailable because the hosted API returned 404 for the comments list endpoint.",
        limit,
        offset,
      );
    }

    throw error;
  });
}
