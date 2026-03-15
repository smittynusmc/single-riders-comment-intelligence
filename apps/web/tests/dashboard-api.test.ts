import { describe, expect, it, vi } from "vitest";

import { ApiRequestError } from "@/lib/api/client";
import { getAudienceInsights, getDashboardSummary, getDashboardTrends, getTopSignals } from "@/lib/api/dashboard";

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    apiFetch: vi.fn(),
  };
});

vi.mock("@/lib/api/signals", () => ({
  getSignals: vi.fn(),
}));

describe("getTopSignals", () => {
  it("falls back to the signals endpoint when dashboard/top-signals is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");
    const { getSignals } = await import("@/lib/api/signals");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/dashboard/top-signals", 404));
    vi.mocked(getSignals).mockResolvedValueOnce({
      items: [
        {
          id: "signal-1",
          fingerprint: "matching",
          title: "Matching filters",
          summary: "Users want stronger filters.",
          mvp_area: "matching",
          primary_category: "feature_request",
          status: "active",
          evidence_count: 12,
          priority_score: 91,
          first_seen_at: null,
          last_seen_at: null,
          sample_comments: [],
          suggested_backlog_action: "Promote",
          reviewed_at: null,
          reviewed_by: null,
          export_metadata: {},
          created_at: "2026-03-14T00:00:00Z",
          updated_at: "2026-03-14T00:00:00Z",
        },
      ],
      meta: { total: 1, limit: 5, offset: 0 },
    });

    const result = await getTopSignals();

    expect(result).toEqual([
      {
        id: "signal-1",
        title: "Matching filters",
        mvp_area: "matching",
        evidence_count: 12,
        priority_score: 91,
      },
    ]);
    expect(getSignals).toHaveBeenCalledWith({ limit: 5 });
  });

  it("returns an empty state when both top-signals endpoints are unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");
    const { getSignals } = await import("@/lib/api/signals");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/dashboard/top-signals", 404));
    vi.mocked(getSignals).mockRejectedValueOnce(new ApiRequestError("/signals?limit=5", 404));

    await expect(getTopSignals()).resolves.toEqual([]);
    expect(getSignals).toHaveBeenCalledWith({ limit: 5 });
  });
});

describe("getDashboardTrends", () => {
  it("falls back to an empty trend set when dashboard/trends is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/dashboard/trends", 404));

    await expect(getDashboardTrends()).resolves.toEqual([]);
  });
});

describe("getDashboardSummary", () => {
  it("falls back to an empty summary when dashboard/summary is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/dashboard/summary", 404));

    await expect(getDashboardSummary()).resolves.toEqual({
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
    });
  });
});

describe("getAudienceInsights", () => {
  it("falls back to empty audience insights when the dashboard audience endpoint is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/dashboard/audience-insights", 404));

    await expect(getAudienceInsights()).resolves.toEqual({
      mvp_priorities: [],
      user_concerns: [],
      confusion_points: [],
      positive_validation: [],
      story_alignment: [],
      top_videos: [],
    });
  });
});
