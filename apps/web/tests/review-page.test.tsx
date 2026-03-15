import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import ReviewQueuePage from "@/app/review/page";

vi.mock("@/lib/api/classifications", () => ({
  getClassifications: vi.fn().mockResolvedValue({
    items: [],
    meta: { total: 0, limit: 100, offset: 0 },
    warning: "Classification data is temporarily unavailable because the hosted API returned 404 for the classifications endpoint.",
  }),
  updateClassification: vi.fn(),
}));

describe("ReviewQueuePage", () => {
  it("renders an empty-state message when the review queue has no items", async () => {
    render(await ReviewQueuePage());

    expect(screen.getByText("Human Review Queue")).toBeInTheDocument();
    expect(screen.getByText(/some data could not be loaded/i)).toBeInTheDocument();
    expect(screen.getByText(/no classifications are available yet/i)).toBeInTheDocument();
  });
});
