import type { PaginatedResponse, Signal, SignalDetail, SignalExportResponse } from "@single-riders/shared-types";

import { apiFetch, buildQuery } from "@/lib/api/client";

export function getSignals(params: Record<string, string | number | boolean | undefined | null> = {}) {
  return apiFetch<PaginatedResponse<Signal>>(`/signals${buildQuery(params)}`);
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
