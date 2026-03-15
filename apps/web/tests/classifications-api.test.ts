import { describe, expect, it, vi } from "vitest";

import { ApiRequestError } from "@/lib/api/client";
import { getClassifications } from "@/lib/api/classifications";

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    apiFetch: vi.fn(),
  };
});

describe("getClassifications", () => {
  it("falls back to an empty review queue when the classifications endpoint is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/classifications?needs_human_review=true&limit=100", 404));

    await expect(getClassifications({ needs_human_review: true, limit: 100 })).resolves.toEqual({
      items: [],
      meta: { total: 0, limit: 100, offset: 0 },
      warning: "Classification data is temporarily unavailable because the hosted API returned 404 for the classifications endpoint.",
    });
  });
});
