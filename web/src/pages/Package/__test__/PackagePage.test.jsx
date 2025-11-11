import { describe, expect, it } from "vitest";

import { render, screen } from "../../../utils/__tests__/test-utils";
import { Package } from "../PackagePage";

describe("Package Component Behavior", () => {
  it("should render correctly on initial load", () => {
    render(<Package />);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
