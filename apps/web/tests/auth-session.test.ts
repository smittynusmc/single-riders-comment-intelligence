import { describe, expect, it } from "vitest";
import { webcrypto } from "node:crypto";

import { createSessionToken, parseAllowedUserEmails, verifySessionToken } from "@/lib/auth/session";

describe("auth session helpers", () => {
  it("parses allowlisted emails and round-trips a signed session", async () => {
    Object.defineProperty(globalThis, "crypto", {
      value: webcrypto,
      configurable: true,
    });
    process.env.AUTH_ALLOWED_USER_EMAILS = "adam@example.com, joe@example.com";
    process.env.AUTH_SESSION_SECRET = "test-session-secret-which-is-long-enough";

    expect(parseAllowedUserEmails()).toEqual(["adam@example.com", "joe@example.com"]);

    const { token, session } = await createSessionToken("Adam@example.com");
    const verifiedSession = await verifySessionToken(token);

    expect(session.email).toBe("adam@example.com");
    expect(session.display_name).toBe("Adam");
    expect(verifiedSession?.email).toBe("adam@example.com");
  });
});
