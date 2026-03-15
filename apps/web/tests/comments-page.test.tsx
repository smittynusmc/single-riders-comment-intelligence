import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import CommentsPage from "@/app/comments/page";

vi.mock("@/lib/api/comments", () => ({
  getComments: vi.fn().mockResolvedValue({
    items: Array.from({ length: 84 }, () => ({})),
    meta: { total: 84, limit: 100, offset: 0 },
    warning: undefined,
  }),
}));

vi.mock("@/lib/api/dashboard", () => ({
  getDashboardSummary: vi.fn().mockResolvedValue({
    total_comments: 84,
    comments_this_week: 1,
    needs_review_count: 0,
    total_signals: 3,
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
}));

vi.mock("@/components/comments/comments-table", () => ({
  CommentsTable: () => <div>Comments Table Mock</div>,
}));

describe("CommentsPage", () => {
  it("renders date coverage and the current filter range", async () => {
    render(
      await CommentsPage({
        searchParams: Promise.resolve({
          date_from: "2025-07-01",
          date_to: "2026-03-31",
        }),
      }),
    );

    expect(screen.getByText("Comments Explorer")).toBeInTheDocument();
    expect(screen.getByText("Date Coverage")).toBeInTheDocument();
    expect(screen.getByText("Jul 1, 2025 to Mar 31, 2026")).toBeInTheDocument();
    expect(screen.getByText("84 comments in the current view.")).toBeInTheDocument();
    expect(screen.getByText("Comments Table Mock")).toBeInTheDocument();
  });

  it("shows all imported data when no date filters are active", async () => {
    render(
      await CommentsPage({
        searchParams: Promise.resolve({}),
      }),
    );

    expect(screen.getByText("All imported data")).toBeInTheDocument();
    expect(screen.getByText("No active filters. Showing all imported data.")).toBeInTheDocument();
  });
});
