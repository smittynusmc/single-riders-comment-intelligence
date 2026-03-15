import type { AudienceInsights, DashboardSummary, TopSignalSummary, TrendPoint } from "@single-riders/shared-types";

import { ApiRequestError, apiFetch } from "@/lib/api/client";
import { getSignals } from "@/lib/api/signals";

const emptyDashboardSummary: DashboardSummary = {
  total_comments: 0,
  comments_this_week: 0,
  needs_review_count: 0,
  total_signals: 0,
  earliest_comment_date: null,
  latest_comment_date: null,
  months_represented: 0,
  top_categories: [],
  top_mvp_areas: [],
  top_repeated_requests: [],
  top_safety_concerns: [],
  top_user_concerns: [],
  top_confusion_points: [],
  top_positive_validation: [],
};

const emptyAudienceInsights: AudienceInsights = {
  mvp_priorities: [],
  user_concerns: [],
  confusion_points: [],
  positive_validation: [],
  story_alignment: [],
  top_videos: [],
};

export async function getDashboardSummary() {
  try {
    return await apiFetch<DashboardSummary>("/dashboard/summary");
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      return emptyDashboardSummary;
    }

    throw error;
  }
}

export async function getDashboardTrends() {
  try {
    return await apiFetch<TrendPoint[]>("/dashboard/trends");
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      return [];
    }

    throw error;
  }
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

export async function getAudienceInsights() {
  try {
    return await apiFetch<AudienceInsights>("/dashboard/audience-insights");
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      return emptyAudienceInsights;
    }

    throw error;
  }
}
