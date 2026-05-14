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

    expect(cropRect).toEqual({
      sx: 0,
      sy: 666.6666666666667,
      sWidth: 1000,
      sHeight: 666.6666666666666,
    });
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
