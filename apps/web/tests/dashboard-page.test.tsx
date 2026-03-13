import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";

vi.mock("@/lib/api/dashboard", () => ({
  getDashboardSummary: vi.fn().mockResolvedValue({
    total_comments: 120,
    comments_this_week: 28,
    needs_review_count: 4,
    total_signals: 7,
    top_categories: [],
    top_mvp_areas: [],
    top_repeated_requests: [],
    top_safety_concerns: [],
  }),
  getDashboardTrends: vi.fn().mockResolvedValue([{ bucket: "2026-03-01", comments: 5, review_queue: 1 }]),
  getTopSignals: vi.fn().mockResolvedValue([{ id: "sig-1", title: "Meetups signal", mvp_area: "meetups", evidence_count: 3, priority_score: 82 }]),
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
  });
});
