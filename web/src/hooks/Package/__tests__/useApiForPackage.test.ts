import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  usePackageDependencies,
  usePackageTicketCounts,
  usePackageVulnIds,
} from "../useApiForPackage";
import {
  useGetDependencies,
  useGetTicketCounts,
  useGetTickets,
  useGetVulnIds,
} from "../useApiForVulnerabilityTable";
import {
  useGetDependenciesQuery,
  useGetPteamTicketsQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
} from "../../../services/tcApi";

vi.mock("../../auth", () => ({
  useSkipUntilAuthUserIsReady: vi.fn(() => false),
}));

vi.mock("../../../services/tcApi", () => ({
  useGetDependenciesQuery: vi.fn(() => ({})),
  useGetPteamTicketsQuery: vi.fn(() => ({})),
  useGetPTeamTicketCountsTiedToServicePackageQuery: vi.fn(() => ({})),
  useGetPTeamVulnIdsTiedToServicePackageQuery: vi.fn(() => ({})),
}));

const packageScope = {
  pteamId: "pteam-1",
  serviceId: "service-1",
  packageVersionId: "package-version-1",
};

describe("Package API hooks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("requests package dependencies by package_version_id", () => {
    renderHook(() => usePackageDependencies(packageScope));

    expect(useGetDependenciesQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          package_version_id: "package-version-1",
          offset: 0,
          limit: 1000,
        },
      },
      expect.any(Object),
    );
    expect(useGetDependenciesQuery).not.toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({ package_id: expect.anything() }),
      }),
      expect.anything(),
    );
  });

  it("requests package vuln ids by package_version_id", () => {
    renderHook(() => usePackageVulnIds({ ...packageScope, relatedTicketStatus: "unsolved" }));

    expect(useGetPTeamVulnIdsTiedToServicePackageQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          package_version_id: "package-version-1",
          related_ticket_status: "unsolved",
        },
      },
      expect.any(Object),
    );
    expect(useGetPTeamVulnIdsTiedToServicePackageQuery).not.toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({ package_id: expect.anything() }),
      }),
      expect.anything(),
    );
  });

  it("requests package ticket counts by package_version_id", () => {
    renderHook(() => usePackageTicketCounts({ ...packageScope, relatedTicketStatus: "solved" }));

    expect(useGetPTeamTicketCountsTiedToServicePackageQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          package_version_id: "package-version-1",
          related_ticket_status: "solved",
        },
      },
      expect.any(Object),
    );
    expect(useGetPTeamTicketCountsTiedToServicePackageQuery).not.toHaveBeenCalledWith(
      expect.objectContaining({
        query: expect.objectContaining({ package_id: expect.anything() }),
      }),
      expect.anything(),
    );
  });

  it("requests vulnerability table data by package_version_id", () => {
    renderHook(() => useGetDependencies(packageScope));
    renderHook(() => useGetVulnIds({ ...packageScope, relatedTicketStatus: "unsolved" }));
    renderHook(() => useGetTicketCounts({ ...packageScope, relatedTicketStatus: "unsolved" }));
    renderHook(() => useGetTickets({ ...packageScope, vulnId: "vuln-1" }));

    expect(useGetDependenciesQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: { service_id: "service-1", package_version_id: "package-version-1" },
      },
      expect.any(Object),
    );
    expect(useGetPTeamVulnIdsTiedToServicePackageQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          package_version_id: "package-version-1",
          related_ticket_status: "unsolved",
        },
      },
      expect.any(Object),
    );
    expect(useGetPTeamTicketCountsTiedToServicePackageQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          package_version_id: "package-version-1",
          related_ticket_status: "unsolved",
        },
      },
      expect.any(Object),
    );
    expect(useGetPteamTicketsQuery).toHaveBeenCalledWith(
      {
        path: { pteam_id: "pteam-1" },
        query: {
          service_id: "service-1",
          vuln_id: "vuln-1",
          package_version_id: "package-version-1",
        },
      },
      expect.any(Object),
    );
  });
});
