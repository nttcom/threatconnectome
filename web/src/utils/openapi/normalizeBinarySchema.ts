export const normalizeBinarySchema = (node: unknown): void => {
  if (!node || typeof node !== "object") {
    return;
  }

  if (Array.isArray(node)) {
    for (const value of node) {
      normalizeBinarySchema(value);
    }
    return;
  }

  const record = node as Record<string, unknown>;
  if (
    record.type === "string" &&
    record.contentMediaType === "application/octet-stream" &&
    record.format === undefined
  ) {
    record.format = "binary";
  }

  for (const value of Object.values(record)) {
    normalizeBinarySchema(value);
  }
};
