import { describe, it, expect } from "vitest";

import {
  getNationalPhoneNumber,
  isE164Format,
  normalizePhoneNumberToE164,
} from "../phoneNumberUtils";

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

describe("normalizePhoneNumberToE164", () => {
  it("should normalize domestic phone numbers to E.164", () => {
    expect(normalizePhoneNumberToE164("09012345678", "JP")).toBe("+819012345678");
    expect(normalizePhoneNumberToE164("2125550191", "US")).toBe("+12125550191");
    expect(normalizePhoneNumberToE164("07911123456", "GB")).toBe("+447911123456");
    expect(normalizePhoneNumberToE164("01012345678", "CN")).toBe("+861012345678");
    expect(normalizePhoneNumberToE164("01098765432", "KR")).toBe("+821098765432");
  });

  it("should keep valid E.164 phone numbers unchanged", () => {
    expect(normalizePhoneNumberToE164("+819012345678", "JP")).toBe("+819012345678");
  });

  it("should return null for invalid phone numbers", () => {
    expect(normalizePhoneNumberToE164("123", "JP")).toBe(null);
    expect(normalizePhoneNumberToE164("", "JP")).toBe(null);
  });
});

describe("getNationalPhoneNumber", () => {
  it("should return national numbers without the country calling code", () => {
    expect(getNationalPhoneNumber("+819012345678")).toBe("9012345678");
    expect(getNationalPhoneNumber("+12125550191")).toBe("2125550191");
  });

  it("should parse domestic input using the default country", () => {
    expect(getNationalPhoneNumber("09012345678", "JP")).toBe("9012345678");
  });

  it("should return null for invalid phone numbers", () => {
    expect(getNationalPhoneNumber("123", "JP")).toBe(null);
  });
});
