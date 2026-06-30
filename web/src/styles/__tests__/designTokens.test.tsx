// @ts-nocheck
import { colors } from "../../pages/App/Topbar/topbarStyles";
import { slate, statusCardSx, uiRadii } from "../../pages/Status/SBOMManagement/styleTokens";
import { uiPalette, uiShadows } from "../designTokens";

describe("designTokens", () => {
  it("keeps Topbar color exports aligned with shared token values", () => {
    expect(colors.ink900).toBe(uiPalette.gray[900]);
    expect(colors.slate200).toBe(uiPalette.slate[200]);
    expect(colors.brand700).toBe(uiPalette.brand[700]);
  });

  it("keeps Status style exports aligned with shared token values", () => {
    expect(slate).toBe(uiPalette.slate);
    expect(statusCardSx.borderRadius).toBe(uiRadii.statusCard);
    expect(uiShadows.xs).toBe("0 1px 2px rgba(15, 23, 42, 0.05)");
  });
});
