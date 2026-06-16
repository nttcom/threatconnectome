import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { defineConfig } from "@hey-api/openapi-ts";
import { normalizeBinarySchema } from "./src/utils/openapi/normalizeBinarySchema";

const openApiDocument = JSON.parse(
  readFileSync(fileURLToPath(new URL("./openapi.json", import.meta.url)), "utf8"),
) as Record<string, unknown>;

normalizeBinarySchema(openApiDocument);

export default defineConfig({
  input: openApiDocument,
  output: "./types",
});
