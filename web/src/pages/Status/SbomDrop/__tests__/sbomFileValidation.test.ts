import { describe, expect, it } from "vitest";

import { validateSbomFileSelection } from "../sbomFileValidation";

describe("validateSbomFileSelection", () => {
  it("returns { file: null, error: null } when files is null", () => {
    expect(validateSbomFileSelection(null)).toEqual({ file: null, error: null });
  });

  it("returns { file: null, error: null } when files is an empty array", () => {
    expect(validateSbomFileSelection([])).toEqual({ file: null, error: null });
  });

  it("returns alertOnlyOneFile error when multiple files are given", () => {
    const files = [
      new File(["{}"], "a.json", { type: "application/json" }),
      new File(["{}"], "b.json", { type: "application/json" }),
    ];
    expect(validateSbomFileSelection(files)).toEqual({ file: null, error: "alertOnlyOneFile" });
  });

  it("returns alertOnlyJson error when the file does not have a .json extension", () => {
    const files = [new File(["text"], "sbom.txt", { type: "text/plain" })];
    expect(validateSbomFileSelection(files)).toEqual({ file: null, error: "alertOnlyJson" });
  });

  it("returns the file when a single .json file is given", () => {
    const file = new File(["{}"], "sbom.json", { type: "application/json" });
    expect(validateSbomFileSelection([file])).toEqual({ file, error: null });
  });
});
