import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import InsightsPage from "@/app/insights/page";

vi.mock("@/lib/api/dashboard", () => ({
  getAudienceInsights: vi.fn().mockResolvedValue({
    mvp_priorities: [
      {
        key: "safety_and_moderation",
        label: "Safety & Moderation",
        summary: "Trust tooling is a launch requirement.",
        story_anchor: "Supports report-user and moderation stories.",
        evidence_count: 8,
        weighted_score: 90.1,
        recent_evidence_count: 5,
        momentum: 62.5,
        trend_label: "Rising",
        mvp_area: "safety",
        primary_category: "safety_or_trust",
        sample_comments: ["Please add better reporting and safety checks"],
      },
    ],
    user_concerns: [],
    confusion_points: [],
    positive_validation: [],
    story_alignment: [],
    top_videos: [],
  }),
}));

describe("InsightsPage", () => {
  it("renders the audience insights heading and priority data", async () => {
    render(await InsightsPage());

    expect(screen.getByText("MVP Audience Insights")).toBeInTheDocument();
    expect(screen.getByText("What Users Care About Most")).toBeInTheDocument();
    expect(screen.getByText("Safety & Moderation")).toBeInTheDocument();
  });
});
