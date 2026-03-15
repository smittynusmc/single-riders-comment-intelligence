import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import ImportsPage from "@/app/imports/page";

vi.mock("@/lib/api/imports", () => ({
  getImports: vi.fn().mockResolvedValue({
    items: [
      {
        id: "run-1",
        source_type: "json_upload",
        source_platform: "tiktok",
        import_format: "tiktok_json",
        source_label: "comments.json",
        status: "completed",
        total_rows: 10,
        imported_rows: 8,
        duplicate_rows: 1,
        failed_rows: 1,
        started_at: null,
        finished_at: null,
        error_message: null,
        uploaded_by_email: "adam@example.com",
        source_file_content_type: "application/json",
        source_file_size_bytes: 2048,
        source_file_sha256: "sha",
        run_metadata: {},
        created_at: "2026-03-01T00:00:00Z",
        updated_at: "2026-03-01T00:00:00Z",
      },
    ],
    meta: { total: 1, limit: 20, offset: 0 },
  }),
  previewImport: vi.fn(),
}));

describe("ImportsPage", () => {
  it("renders upload and history sections", async () => {
    render(await ImportsPage());

    expect(screen.getByText("Export Upload")).toBeInTheDocument();
    expect(screen.getByText("Import History")).toBeInTheDocument();
    expect(screen.getByText("comments.json")).toBeInTheDocument();
    expect(screen.getByText("tiktok json")).toBeInTheDocument();
    expect(screen.getByText(/uploaded by adam@example.com/i)).toBeInTheDocument();
  });

  it("renders an empty-state message when import history is unavailable", async () => {
    const { getImports } = await import("@/lib/api/imports");
    vi.mocked(getImports).mockResolvedValueOnce({
      items: [],
      meta: { total: 0, limit: 20, offset: 0 },
      warning: "Import history is temporarily unavailable because the hosted API returned 404 for the imports list endpoint.",
    });

    render(await ImportsPage());

    expect(screen.getByText(/some data could not be loaded/i)).toBeInTheDocument();
    expect(screen.getByText(/no imports have been recorded yet/i)).toBeInTheDocument();
  });
});
