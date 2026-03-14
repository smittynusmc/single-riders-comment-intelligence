import type { AudienceInsights, DashboardSummary, TopSignalSummary, TrendPoint } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch } from "@/lib/api/client";
import { getSignals } from "@/lib/api/signals";

export function getDashboardSummary() {
  return apiFetch<DashboardSummary>("/dashboard/summary");
}

export function getDashboardTrends() {
  return apiFetch<TrendPoint[]>("/dashboard/trends");
}

export async function getTopSignals() {
  try {
    return await apiFetch<TopSignalSummary[]>("/dashboard/top-signals");
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      const response = await getSignals({ limit: 5 });
      return response.items.map((signal) => ({
        id: signal.id,
        title: signal.title,
        mvp_area: signal.mvp_area,
        evidence_count: signal.evidence_count,
        priority_score: signal.priority_score,
      }));
    }

    throw error;
  }
}

export function getAudienceInsights() {
  return apiFetch<AudienceInsights>("/dashboard/audience-insights");
}
