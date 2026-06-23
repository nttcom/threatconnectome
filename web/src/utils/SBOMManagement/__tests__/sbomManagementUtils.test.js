import { describe, expect, it } from "vitest";

import {
  buildCurrentServiceFromPTeam,
  buildDependencyRows,
  buildServiceTabsFromPTeam,
  isDeleteConfirmationValid,
  normalizeCommaSeparatedValues,
} from "../sbomManagementUtils";

const services = [
  {
    service_id: "service-1",
    service_name: "Service One",
    description: "Primary service",
    keywords: ["prod", "api"],
    system_exposure: "controlled",
    service_mission_impact: "mef_failure",
    asset: {
      ip_addresses: ["10.0.0.1", "10.0.0.2"],
      country_code: "JP",
      address: "Tokyo",
    },
  },
  {
    service_id: "service-2",
    service_name: "Service Two",
    description: null,
    keywords: [],
    system_exposure: "open",
    service_mission_impact: "mission_failure",
  },
];

const packages = [
  {
    package_id: "package-1",
    package_version_id: "package-version-1",
    package_name: "react",
    package_version: "19.1.0",
    ecosystem: "npm",
    ssvc_priority: "scheduled",
  },
  {
    package_id: "package-2",
    package_version_id: "package-version-2",
    package_name: "sqlparse",
    package_version: "0.5.3",
    ecosystem: "pypi",
    ssvc_priority: null,
  },
];

describe("sbomManagementUtils", () => {
  it("normalizes comma-separated values by trimming and dropping empty items", () => {
    expect(normalizeCommaSeparatedValues(" a, ,b ,")).toEqual(["a", "b"]);
  });

  it("builds tab data without per-service details", () => {
    expect(buildServiceTabsFromPTeam(services)).toEqual([
      { id: "service-1", title: "Service One" },
      { id: "service-2", title: "Service Two" },
    ]);
  });

  it("builds only the current service details", () => {
    expect(
      buildCurrentServiceFromPTeam(services, "service-1", "data:image/png;base64,abc"),
    ).toEqual({
      id: "service-1",
      title: "Service One",
      description: "Primary service",
      tags: ["prod", "api"],
      systemExposure: "controlled",
      missionImpact: "mef_failure",
      imageUrl: "data:image/png;base64,abc",
      ipAddresses: ["10.0.0.1", "10.0.0.2"],
      countryCode: "JP",
      address: "Tokyo",
    });
  });

  it("builds empty asset details when the current service has no asset", () => {
    expect(buildCurrentServiceFromPTeam(services, "service-2")).toMatchObject({
      ipAddresses: [],
      countryCode: "",
      address: "",
    });
  });

  it("returns null when the current service is not present", () => {
    expect(buildCurrentServiceFromPTeam(services, "missing-service")).toBeNull();
  });

  it("builds dependency rows for only the current service", () => {
    expect(buildDependencyRows(packages, "service-1")).toEqual([
      {
        packageVersionId: "package-version-1",
        serviceId: "service-1",
        name: "react",
        version: "19.1.0",
        type: "npm",
        license: "",
        ssvcPriority: "scheduled",
      },
      {
        packageVersionId: "package-version-2",
        serviceId: "service-1",
        name: "sqlparse",
        version: "0.5.3",
        type: "pypi",
        license: "",
        ssvcPriority: "no_known_vulnerability",
      },
    ]);
  });
});

describe("isDeleteConfirmationValid", () => {
  it("returns true when input matches title exactly", () => {
    expect(isDeleteConfirmationValid("My Service", "My Service")).toBe(true);
  });

  it("returns false when input does not match title", () => {
    expect(isDeleteConfirmationValid("Other Service", "My Service")).toBe(false);
  });

  it("trims leading and trailing whitespace from input", () => {
    expect(isDeleteConfirmationValid("  My Service  ", "My Service")).toBe(true);
  });

  it("returns false when input is empty", () => {
    expect(isDeleteConfirmationValid("", "My Service")).toBe(false);
  });

  it("returns false when input is only whitespace", () => {
    expect(isDeleteConfirmationValid("   ", "My Service")).toBe(false);
  });
});
