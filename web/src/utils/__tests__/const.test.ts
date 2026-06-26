import { describe, expect, it } from "vitest";

import { getExperienceBucket } from "../const";

describe("getExperienceBucket", () => {
  it.each([
    [0, 0],
    [1, 0],
    [2, 2],
    [4, 2],
    [5, 5],
    [6, 5],
    [7, 7],
    [10, 7],
  ])("maps %i years to bucket %i", (years, bucket) => {
    expect(getExperienceBucket(years)).toBe(bucket);
  });
});
