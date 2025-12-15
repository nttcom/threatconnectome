import { describe, it, expect } from "vitest";
import { isE164Format } from "../phoneNumberUtils";

describe("isValidE164", () => {
  it("should return true for valid E.164 numbers", () => {
    expect(isE164Format("+819012345678")).toBe(true);
    expect(isE164Format("+81312345678")).toBe(true);
    expect(isE164Format("+12125550191")).toBe(true);
    expect(isE164Format("+14155552671")).toBe(true);
    expect(isE164Format("+442079460958")).toBe(true);
    expect(isE164Format("+447911123456")).toBe(true);
    expect(isE164Format("+861012345678")).toBe(true);
    expect(isE164Format("+862187654321")).toBe(true);
    expect(isE164Format("+82212345678")).toBe(true);
    expect(isE164Format("+821098765432")).toBe(true);
  });

  it("should return false for invalid E.164 numbers", () => {
    expect(isE164Format("819012345678")).toBe(false);
    expect(isE164Format("+81-90-1234-5678")).toBe(false);
    expect(isE164Format("+81abcde")).toBe(false);
    expect(isE164Format("")).toBe(false);
    expect(isE164Format("+81090123456789")).toBe(false);
  });
});
