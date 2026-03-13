import type { IngestionRun, PaginatedResponse } from "@single-riders/shared-types";

import { apiFetch, buildQuery } from "@/lib/api/client";

export function getImports(params: { limit?: number; offset?: number } = {}) {
  return apiFetch<PaginatedResponse<IngestionRun>>(`/imports${buildQuery(params)}`);
}
