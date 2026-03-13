import type { DashboardSummary, TopSignalSummary, TrendPoint } from "@single-riders/shared-types";

import { apiFetch } from "@/lib/api/client";

export function getDashboardSummary() {
  return apiFetch<DashboardSummary>("/dashboard/summary");
}

export function getDashboardTrends() {
  return apiFetch<TrendPoint[]>("/dashboard/trends");
}

export function getTopSignals() {
  return apiFetch<TopSignalSummary[]>("/dashboard/top-signals");
}
