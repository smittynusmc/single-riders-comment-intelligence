import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import ImportsPage from "@/app/imports/page";

vi.mock("@/lib/api/imports", () => ({
  getImports: vi.fn().mockResolvedValue({
    items: [
      {
        id: "run-1",
        source_type: "csv",
        source_platform: "tiktok",
        source_label: "comments.csv",
        status: "completed",
        total_rows: 10,
        imported_rows: 8,
        duplicate_rows: 1,
        failed_rows: 1,
        started_at: null,
        finished_at: null,
        error_message: null,
        run_metadata: {},
        created_at: "2026-03-01T00:00:00Z",
        updated_at: "2026-03-01T00:00:00Z",
      },
    ],
    meta: { total: 1, limit: 20, offset: 0 },
  }),
}));

describe("ImportsPage", () => {
  it("renders upload and history sections", async () => {
    render(await ImportsPage());

    expect(screen.getByText("CSV Upload")).toBeInTheDocument();
    expect(screen.getByText("Import History")).toBeInTheDocument();
    expect(screen.getByText("comments.csv")).toBeInTheDocument();
  });
});
