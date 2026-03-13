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

describe("SignalsPage", () => {
  it("renders signal cards from API data", async () => {
    render(await SignalsPage());

    expect(screen.getByText("Signals")).toBeInTheDocument();
    expect(screen.getByText("Meetups: repeated meetup signal")).toBeInTheDocument();
    expect(screen.getByText("Export GitHub")).toBeInTheDocument();
  });
});
