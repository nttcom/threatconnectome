export type SbomFileValidationError = "alertOnlyOneFile" | "alertOnlyJson";

type SbomFileValidationResult =
  | { file: File; error: null }
  | { file: null; error: SbomFileValidationError | null };

export function validateSbomFileSelection(
  files: FileList | File[] | null,
): SbomFileValidationResult {
  if (!files || !files.length) return { file: null, error: null };
  if (files.length > 1) return { file: null, error: "alertOnlyOneFile" };
  if (!files[0].name.endsWith(".json")) return { file: null, error: "alertOnlyJson" };
  return { file: files[0], error: null };
}
