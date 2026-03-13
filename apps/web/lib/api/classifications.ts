import type { ClassificationReviewItem, CommentClassification, PaginatedResponse } from "@single-riders/shared-types";

import { apiFetch, buildQuery } from "@/lib/api/client";

export function getClassifications(params: Record<string, string | number | boolean | undefined | null>) {
  return apiFetch<PaginatedResponse<ClassificationReviewItem>>(`/classifications${buildQuery(params)}`);
}

export function updateClassification(classificationId: string, payload: Record<string, unknown>) {
  return apiFetch<CommentClassification>(`/classifications/${classificationId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
