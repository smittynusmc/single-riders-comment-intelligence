import type { ImportPreview, IngestionRun, PaginatedResponse } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch, apiUpload, buildQuery } from "@/lib/api/client";

export function getImports(params: { limit?: number; offset?: number } = {}) {
  const limit = params.limit ?? 50;
  const offset = params.offset ?? 0;

  return apiFetch<PaginatedResponse<IngestionRun>>(`/imports${buildQuery(params)}`).catch((error) => {
    if (error instanceof ApiRequestError && error.status === 404) {
      return {
        items: [],
        meta: { total: 0, limit, offset },
      };
    }

    throw error;
  });
}

export function previewImport(formData: FormData) {
  return apiUpload<ImportPreview>("/imports/preview", formData);
}
