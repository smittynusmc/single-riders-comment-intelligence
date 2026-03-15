import type { ImportPreview, IngestionRun, PaginatedResponse } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch, apiUpload, buildQuery } from "@/lib/api/client";
import { buildUnavailablePaginatedResponse, type FallbackPaginatedResponse } from "@/lib/api/fallback";

export function getImports(params: { limit?: number; offset?: number } = {}): Promise<FallbackPaginatedResponse<IngestionRun>> {
  const limit = params.limit ?? 50;
  const offset = params.offset ?? 0;

  return apiFetch<PaginatedResponse<IngestionRun>>(`/imports${buildQuery(params)}`).catch((error): FallbackPaginatedResponse<IngestionRun> => {
    if (error instanceof ApiRequestError && error.status === 404) {
      return buildUnavailablePaginatedResponse(
        "Import history is temporarily unavailable because the hosted API returned 404 for the imports list endpoint.",
        limit,
        offset,
      );
    }

    throw error;
  });
}

export function previewImport(formData: FormData) {
  return apiUpload<ImportPreview>("/imports/preview", formData);
}
