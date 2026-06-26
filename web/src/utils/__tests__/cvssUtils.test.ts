import { describe, expect, it } from "vitest";

import { cvssConvertToName } from "../cvssUtils";

describe("cvssConvertToName", () => {
  it("keeps an explicit zero score in the None rating", () => {
    expect(cvssConvertToName(0)).toBe("None");
  });

  it("keeps missing scores in the fallback None rating", () => {
    expect(cvssConvertToName("N/A")).toBe("None");
    expect(cvssConvertToName(null)).toBe("None");
    expect(cvssConvertToName(undefined)).toBe("None");
  });
});
