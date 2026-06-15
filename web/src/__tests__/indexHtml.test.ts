import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const indexHtml = readFileSync(join(process.cwd(), "index.html"), "utf8");

describe("index.html", () => {
  it("declares the SVG favicon as scalable", () => {
    const document = new DOMParser().parseFromString(indexHtml, "text/html");
    const favicon = document.querySelector('link[rel="icon"]');

    expect(favicon?.getAttribute("type")).toBe("image/svg+xml");
    expect(favicon?.getAttribute("sizes")).toBe("any");
    expect(favicon?.getAttribute("href")).toBe("/favicon.svg");
  });
});
