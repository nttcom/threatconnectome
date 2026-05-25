import { describe, expect, it } from "vitest";

import { calculateCenteredCropRect } from "../serviceImageUtils";

describe("calculateCenteredCropRect", () => {
  it("crops left and right sides when source image is wider than 4:3", () => {
    const cropRect = calculateCenteredCropRect(2000, 1000, 720, 480);

    expect(cropRect).toEqual({
      sx: 250,
      sy: 0,
      sWidth: 1500,
      sHeight: 1000,
    });
  });

  it("crops top and bottom when source image is taller than 4:3", () => {
    const cropRect = calculateCenteredCropRect(1000, 2000, 720, 480);

    expect(cropRect.sx).toBe(0);
    expect(cropRect.sy).toBeCloseTo(666.667, 2);
    expect(cropRect.sWidth).toBe(1000);
    expect(cropRect.sHeight).toBeCloseTo(666.667, 2);
  });

  it("keeps dimensions when source image already has 4:3 ratio", () => {
    const cropRect = calculateCenteredCropRect(720, 480, 720, 480);

    expect(cropRect).toEqual({
      sx: 0,
      sy: 0,
      sWidth: 720,
      sHeight: 480,
    });
  });
});
