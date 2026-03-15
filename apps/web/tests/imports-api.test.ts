import { describe, expect, it, vi } from "vitest";

import { ApiRequestError } from "@/lib/api/client";
import { getImports } from "@/lib/api/imports";

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    apiFetch: vi.fn(),
  };
});

describe("getImports", () => {
  it("falls back to an empty import history when the imports endpoint is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/imports?limit=20", 404));

    await expect(getImports({ limit: 20 })).resolves.toEqual({
      items: [],
      meta: { total: 0, limit: 20, offset: 0 },
      warning: "Import history is temporarily unavailable because the hosted API returned 404 for the imports list endpoint.",
    });
  });
});
