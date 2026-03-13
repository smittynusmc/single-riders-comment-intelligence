import type { ImportPreview, IngestionRun, PaginatedResponse } from "@single-riders/shared-types";

import { apiFetch, apiUpload, buildQuery } from "@/lib/api/client";

export function getImports(params: { limit?: number; offset?: number } = {}) {
  return apiFetch<PaginatedResponse<IngestionRun>>(`/imports${buildQuery(params)}`);
}

export function previewImport(formData: FormData) {
  return apiUpload<ImportPreview>("/imports/preview", formData);
}
