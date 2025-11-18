import { vi } from "vitest";

import {
  useGetDependenciesQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPteamTicketsQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetUserMeQuery,
  useGetVulnActionsQuery,
  useGetVulnQuery,
} from "../../../services/tcApi";

export const MOCK_PTEAM = {
  pteam_id: "pteam-abc",
  pteam_name: "PTeam Alpha",
  services: [{ service_id: "svc-xyz", service_name: "Test Service" }],
  tags: [],
};
export const MOCK_DEPENDENCIES = [
  {
    dependency_id: "dep-123",
    target: "target-file.txt",
    package_name: "react",
    package_version: "18.2.0",
    package_source_name: "npm",
    package_manager: "npm",
    package_ecosystem: "npm",
    vuln_matching_ecosystem: "npm",
  },
];
export const MOCK_VULN_IDS_SOLVED = { vuln_ids: ["CVE-2023-0001"] };
export const MOCK_VULN_IDS_UNSOLVED = { vuln_ids: ["CVE-2023-0002", "CVE-2023-0003"] };
export const MOCK_TICKET_COUNTS_SOLVED = { ssvc_priority_count: [{ priority: "high", count: 1 }] };
export const MOCK_TICKET_COUNTS_UNSOLVED = {
  ssvc_priority_count: [{ priority: "critical", count: 2 }],
};

export function setupApiMocks() {
  vi.mocked(useGetDependenciesQuery).mockReturnValue({
    data: MOCK_DEPENDENCIES,
    isLoading: false,
    isSuccess: true,
  });

  vi.mocked(useGetPTeamQuery).mockReturnValue({
    data: MOCK_PTEAM,
    isLoading: false,
    isSuccess: true,
  });
  vi.mocked(useGetPTeamVulnIdsTiedToServicePackageQuery).mockImplementation((args) => {
    if (args.relatedTicketStatus === "solved") {
      return { data: MOCK_VULN_IDS_SOLVED, isLoading: false, isSuccess: true };
    }
    return { data: MOCK_VULN_IDS_UNSOLVED, isLoading: false, isSuccess: true };
  });
  vi.mocked(useGetPTeamTicketCountsTiedToServicePackageQuery).mockImplementation((args) => {
    if (args.relatedTicketStatus === "solved") {
      return { data: MOCK_TICKET_COUNTS_SOLVED, isLoading: false, isSuccess: true };
    }
    return { data: MOCK_TICKET_COUNTS_UNSOLVED, isLoading: false, isSuccess: true };
  });

  vi.mocked(useGetPTeamMembersQuery).mockReturnValue({
    data: [],
    isLoading: false,
    isSuccess: true,
  });
  vi.mocked(useGetVulnQuery).mockImplementation(({ vulnId }) => ({
    data: {
      vulnerability_id: vulnId,
      title: `Vulnerability ${vulnId}`,
      updated_at: "2023-10-27T10:00:00.000Z",
      vulnerable_packages: [
        {
          affected_name: "react",
          ecosystem: "npm",
          affected_versions: ["18.2.0"],
          fixed_versions: ["18.2.1"],
        },
      ],
    },
    isLoading: false,
    isSuccess: true,
  }));
  vi.mocked(useGetVulnActionsQuery).mockReturnValue({
    data: [],
    isLoading: false,
    isSuccess: true,
  });
  vi.mocked(useGetPteamTicketsQuery).mockImplementation((args) => {
    const vulnId = args?.vulnId || "unknown";
    return {
      data: [
        {
          ticket_id: `ticket-for-${vulnId}`,
          ssvc_deployer_priority: "Immediate",
          ticket_status: {
            ticket_handling_status: "alerted",
            assignees: [],
          },
        },
      ],
      isLoading: false,
      isSuccess: true,
    };
  });
  vi.mocked(useGetUserMeQuery).mockReturnValue({
    data: { user_id: "test-user-id" },
    isLoading: false,
    isSuccess: true,
  });
}
