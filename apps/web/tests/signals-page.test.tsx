import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import SignalsPage from "@/app/signals/page";

vi.mock("@/lib/api/signals", () => ({
  getSignals: vi.fn().mockResolvedValue({
    items: [
      {
        id: "signal-1",
        fingerprint: "meetups:social_coordination:meetup",
        title: "Meetups: repeated meetup signal",
        summary: "3 comments point to meetup planning demand.",
        mvp_area: "meetups",
        primary_category: "social_coordination",
        status: "active",
        evidence_count: 3,
        priority_score: 81,
        first_seen_at: "2026-03-01T00:00:00Z",
        last_seen_at: "2026-03-02T00:00:00Z",
        sample_comments: [{ text: "Need meetup planning" }],
        suggested_backlog_action: "Build meetup planning.",
        reviewed_at: null,
        reviewed_by: null,
        export_metadata: {},
        created_at: "2026-03-02T00:00:00Z",
        updated_at: "2026-03-02T00:00:00Z",
      },
    ],
    meta: { total: 1, limit: 50, offset: 0 },
  }),
}));

vi.mock("@/lib/api/dashboard", () => ({
  getAudienceInsights: vi.fn().mockResolvedValue({
    mvp_priorities: [
      {
        key: "park_day_coordination",
        label: "Park-Day Coordination",
        summary: "Same-day planning demand is rising.",
        story_anchor: "Supports meetup planning stories.",
        evidence_count: 7,
        weighted_score: 84.2,
        recent_evidence_count: 3,
        momentum: 42.8,
        trend_label: "Rising",
        mvp_area: "meetups",
        primary_category: "social_coordination",
        sample_comments: ["Need same-day meetup planning"],
      },
    ],
    user_concerns: [],
    confusion_points: [],
    positive_validation: [],
    story_alignment: [],
    top_videos: [],
  }),
}));

describe("SignalsPage", () => {
  it("renders signal cards from API data", async () => {
    render(await SignalsPage());

    expect(screen.getByText("Signals")).toBeInTheDocument();
    expect(screen.getByText("Meetups: repeated meetup signal")).toBeInTheDocument();
    expect(screen.getByText("Export GitHub")).toBeInTheDocument();
    expect(screen.getByText("Audience Priorities Beside The Signal Queue")).toBeInTheDocument();
  });

  it("renders an empty-state message when no signals are available", async () => {
    const { getSignals } = await import("@/lib/api/signals");

    vi.mocked(getSignals).mockResolvedValueOnce({
      items: [],
      meta: { total: 0, limit: 50, offset: 0 },
      warning: "Signals are temporarily unavailable because the hosted API returned 404 for the signals list endpoint.",
    });

    render(await SignalsPage());

    expect(screen.getByText(/some data could not be loaded/i)).toBeInTheDocument();
    expect(screen.getByText(/no signals are available yet/i)).toBeInTheDocument();
  });
});
