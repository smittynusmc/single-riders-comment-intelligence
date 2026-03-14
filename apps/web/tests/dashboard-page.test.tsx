import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";

vi.mock("@/lib/api/dashboard", () => ({
  getDashboardSummary: vi.fn().mockResolvedValue({
    total_comments: 120,
    comments_this_week: 28,
    needs_review_count: 4,
    total_signals: 7,
    earliest_comment_date: "2025-07-08T11:22:02Z",
    latest_comment_date: "2026-03-07T22:36:43Z",
    months_represented: 9,
    top_categories: [],
    top_mvp_areas: [],
    top_repeated_requests: [],
    top_safety_concerns: [],
    top_user_concerns: [],
    top_confusion_points: [],
    top_positive_validation: [],
  }),
  getDashboardTrends: vi.fn().mockResolvedValue([{ bucket: "2026-03-01", comments: 5, review_queue: 1 }]),
  getTopSignals: vi.fn().mockResolvedValue([{ id: "sig-1", title: "Meetups signal", mvp_area: "meetups", evidence_count: 3, priority_score: 82 }]),
  getAudienceInsights: vi.fn().mockResolvedValue({
    mvp_priorities: [
      {
        key: "matching_and_filters",
        label: "Matching & Filters",
        summary: "Users care about matching quality.",
        story_anchor: "Supports matching stories.",
        evidence_count: 9,
        weighted_score: 87.4,
        recent_evidence_count: 4,
        momentum: 44.4,
        trend_label: "Rising",
        mvp_area: "matching",
        primary_category: "feature_request",
        sample_comments: ["Need better filters"],
      },
    ],
    user_concerns: [],
    confusion_points: [],
    positive_validation: [],
    story_alignment: [],
    top_videos: [],
  }),
}));

vi.mock("@/components/dashboard/trend-chart", () => ({
  TrendChart: () => <div>Trend Chart Mock</div>,
}));

describe("DashboardPage", () => {
  it("renders the dashboard heading and summary values", async () => {
    render(await DashboardPage());

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText("Trend Chart Mock")).toBeInTheDocument();
    expect(screen.getByText("What Users Care About Most For The MVP")).toBeInTheDocument();
    expect(screen.getByText("Matching & Filters")).toBeInTheDocument();
    expect(screen.getByText("Date Coverage")).toBeInTheDocument();
    expect(screen.getByText("9")).toBeInTheDocument();
  });
});
