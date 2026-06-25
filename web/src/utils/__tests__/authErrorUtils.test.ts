import { describe, expect, it } from "vitest";

import { authErrorToString } from "../authErrorUtils";

describe("authErrorToString", () => {
  it("returns an Error message", () => {
    expect(authErrorToString(new Error("Authentication failed"))).toBe("Authentication failed");
  });

  it("returns a string error as-is", () => {
    expect(authErrorToString("Authentication failed")).toBe("Authentication failed");
  });

  it("returns message from message-like objects", () => {
    expect(authErrorToString({ message: "Authentication failed" })).toBe("Authentication failed");
  });

  it("returns undefined when AuthErrorSource has no message", () => {
    expect(authErrorToString({ code: "auth/internal-error" })).toBeUndefined();
  });
});
