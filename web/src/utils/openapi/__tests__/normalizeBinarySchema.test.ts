import { describe, expect, it } from "vitest";

import { normalizeBinarySchema } from "../normalizeBinarySchema";

describe("normalizeBinarySchema", () => {
  it("converts contentMediaType application/octet-stream to format binary", () => {
    const document = {
      components: {
        schemas: {
          UploadRequest: {
            type: "object",
            properties: {
              file: {
                type: "string",
                contentMediaType: "application/octet-stream",
              },
            },
          },
        },
      },
    };

    normalizeBinarySchema(document);

    expect(document.components.schemas.UploadRequest.properties.file).toEqual({
      type: "string",
      contentMediaType: "application/octet-stream",
      format: "binary",
    });
  });

  it("does not overwrite existing format", () => {
    const document = {
      schema: {
        type: "string",
        contentMediaType: "application/octet-stream",
        format: "date-time",
      },
    };

    normalizeBinarySchema(document);

    expect(document.schema.format).toBe("date-time");
  });
});
