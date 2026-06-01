export const collapseSpaces = (s: string | null | undefined): string =>
  s == null ? "" : String(s).replace(/\s+/g, " ");
