import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Package } from "../PackagePage";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: { count?: number }) =>
      options?.count === undefined ? key : `${key}:${options.count}`,
  }),
}));

vi.mock("../../../hooks/auth", () => ({
  useSkipUntilAuthUserIsReady: vi.fn(() => false),
}));

vi.mock("../../../hooks/usePageParams", () => ({
  usePageParams: () => ({
    packageVersionId: "package-version-1",
    pteamId: "pteam-1",
    serviceId: "service-1",
  }),
}));

vi.mock("../../../hooks/Package/useApiForPackage", () => ({
  usePackageService: () => ({
    service: undefined,
    error: undefined,
    isLoading: false,
  }),
  usePackageVulnCounts: () => ({
    solvedVulnCount: 1,
    unsolvedVulnCount: 2,
    solvedError: undefined,
    unsolvedError: undefined,
    solvedLoading: false,
    unsolvedLoading: false,
  }),
  usePackageDependencies: () => ({
    data: [
      {
        dependency_id: "dependency-1",
        target: "package-lock.json",
        package_version: "1.0.0",
        package_name: "example-package",
        package_source_name: null,
        package_manager: "npm",
        package_ecosystem: "npm",
      },
    ],
    error: undefined,
    isLoading: false,
  }),
}));

vi.mock("../CodeBlock", () => ({
  CodeBlock: () => null,
}));

vi.mock("../PackageReferences", () => ({
  PackageReferences: () => <div data-testid="package-references" />,
}));

vi.mock("../VulnerabilityTable/VulnerabilityTable", () => ({
  VulnerabilityTable: () => <div data-testid="vulnerability-table" />,
}));

describe("Package page", () => {
  it("does not fail while pteam service details are temporarily unavailable", () => {
    render(<Package />);

    expect(screen.getByText("example-package")).toBeInTheDocument();
    expect(screen.getByText("service-1")).toBeInTheDocument();
  });
});
