import type { PaginatedResponse, Signal, SignalDetail, SignalExportResponse } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch, buildQuery } from "@/lib/api/client";
import { buildUnavailablePaginatedResponse, type FallbackPaginatedResponse } from "@/lib/api/fallback";

export function getSignals(params: Record<string, string | number | boolean | undefined | null> = {}) {
  const limit = typeof params.limit === "number" ? params.limit : 50;
  const offset = typeof params.offset === "number" ? params.offset : 0;

  return apiFetch<PaginatedResponse<Signal>>(`/signals${buildQuery(params)}`).catch((error): FallbackPaginatedResponse<Signal> => {
    if (error instanceof ApiRequestError && error.status === 404) {
      return buildUnavailablePaginatedResponse(
        "Signals are temporarily unavailable because the hosted API returned 404 for the signals list endpoint.",
        limit,
        offset,
      );
    }

    throw error;
  });
}

export function getSignal(signalId: string) {
  return apiFetch<SignalDetail>(`/signals/${signalId}`);
}

export function rebuildSignals() {
  return apiFetch<{ message: string }>("/signals/rebuild", { method: "POST" });
}

export function updateSignal(signalId: string, payload: Record<string, unknown>) {
  return apiFetch<Signal>(`/signals/${signalId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function exportSignal(signalId: string, destination: "github" | "trello") {
  return apiFetch<SignalExportResponse>(`/signals/${signalId}/export/${destination}`, {
    method: "POST",
  });
}
