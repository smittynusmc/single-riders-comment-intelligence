import type { ClassificationReviewItem, CommentClassification, PaginatedResponse } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch, buildQuery } from "@/lib/api/client";
import { buildUnavailablePaginatedResponse, type FallbackPaginatedResponse } from "@/lib/api/fallback";

export function getClassifications(
  params: Record<string, string | number | boolean | undefined | null>,
): Promise<FallbackPaginatedResponse<ClassificationReviewItem>> {
  const limit = typeof params.limit === "number" ? params.limit : 50;
  const offset = typeof params.offset === "number" ? params.offset : 0;

  return apiFetch<PaginatedResponse<ClassificationReviewItem>>(`/classifications${buildQuery(params)}`).catch(
    (error): FallbackPaginatedResponse<ClassificationReviewItem> => {
      if (error instanceof ApiRequestError && error.status === 404) {
        return buildUnavailablePaginatedResponse(
          "Classification data is temporarily unavailable because the hosted API returned 404 for the classifications endpoint.",
          limit,
          offset,
        );
      }

      throw error;
    },
  );
}

export function updateClassification(classificationId: string, payload: Record<string, unknown>) {
  return apiFetch<CommentClassification>(`/classifications/${classificationId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
