import { describe, it, expect } from "vitest";

import { collapseSpaces } from "../displayText";

describe("collapseSpaces", () => {
  it("collapses multiple spaces into one", () => {
    expect(collapseSpaces("aaa   aaa")).toBe("aaa aaa");
  });

  it("collapses tabs and newlines", () => {
    expect(collapseSpaces("a\t\tb")).toBe("a b");
    expect(collapseSpaces("a\n\nb")).toBe("a b");
  });

  it("leaves single-spaced strings untouched", () => {
    expect(collapseSpaces("aaa aaa")).toBe("aaa aaa");
  });

  it("returns empty string for null and undefined", () => {
    expect(collapseSpaces(null)).toBe("");
    expect(collapseSpaces(undefined)).toBe("");
  });

  it("returns empty string unchanged", () => {
    expect(collapseSpaces("")).toBe("");
  });
});
