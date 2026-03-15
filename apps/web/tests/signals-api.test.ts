import { describe, expect, it, vi } from "vitest";

import { ApiRequestError } from "@/lib/api/client";
import { getSignals } from "@/lib/api/signals";

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    apiFetch: vi.fn(),
  };
});

describe("getSignals", () => {
  it("falls back to an empty signal list when the signals endpoint is unavailable", async () => {
    const { apiFetch } = await import("@/lib/api/client");

    vi.mocked(apiFetch).mockRejectedValueOnce(new ApiRequestError("/signals?limit=50", 404));

    await expect(getSignals({ limit: 50 })).resolves.toEqual({
      items: [],
      meta: { total: 0, limit: 50, offset: 0 },
      warning: "Signals are temporarily unavailable because the hosted API returned 404 for the signals list endpoint.",
    });
  });
});
