import { describe, it, expect } from "vitest";
import { calculateEstimateTimeFromSize } from "../estimator";

describe("calculateEstimateTimeFromSize", () => {
  // Test cases: [sizeInBytes, expectedMinutes]
  it.each([
    [0, 0.0871], // 0 B
    [133 * 1024, 0.4156], // 133 KB (Updated expected value for precision)
    [1024 * 1024, 2.7569], // 1 MB (1024 KB)
    [10240 * 1024, 39.4308], // 10 MB (10240 KB)
    [51200 * 1024, 477.8241], // 50 MB (51200 KB)
  ])(
    "when size is %d Bytes, it should return approximately %d minutes",
    (sizeInBytes, expectedMinutes) => {
      const result = calculateEstimateTimeFromSize(sizeInBytes);

      // Checking if the result is close to the expected minutes with 2-decimal precision
      expect(result).toBeCloseTo(expectedMinutes, 2);
    },
  );
});
