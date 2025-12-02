// Mock data for PackagePage stories (PackagePage-specific data only)
// Shared data (VulnDetails, Dependencies, Tickets) are imported from VulnerabilityTable/mocks

import { http, HttpResponse } from "msw";

import {
  createVulnerabilityTableHandlers,
  mockVulnDetailsForPackagePage,
  mockVulnDetails,
} from "../VulnerabilityTable/mocks/mockData";

export const pteamId = "pteam-abc-123";
export const serviceId = "service-xyz-789";
export const packageId = "pkg-uuid-456";

export const mockPTeam = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  services: [
    { service_id: serviceId, service_name: "My Production Service", service_safety_impact: "high" },
  ],
};

export const mockVulnIdsUnsolved = {
  vuln_ids: ["CVE-2021-44228", "CVE-2022-1234"],
};

export const mockVulnIdsSolved = {
  vuln_ids: ["CVE-2020-5678"],
};

export const mockTicketCountsUnsolved = {
  ssvc_priority_count: {
    immediate: 1,
    out_of_cycle: 1,
    scheduled: 0,
    defer: 0,
  },
};

export const mockTicketCountsSolved = {
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 0,
    scheduled: 1,
    defer: 0,
  },
};

export const mockVulnActions = {
  "CVE-2021-44228": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "CVE-2022-1234": [],
  "CVE-2020-5678": [],
};

export const mockMembersList = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
];

export const mockUserMe = {
  user_id: "current-user-123",
  name: "Current User",
  email: "current.user@example.com",
  pteam_roles: [],
};

export function createPackagePageHandlers(config) {
  const {
    pteamId,
    serviceId,
    packageId,
    mockVulnIdsUnsolved,
    mockVulnIdsSolved,
    mockTicketCountsUnsolved,
    mockTicketCountsSolved,
    mockVulnActions,
    mockMembersList,
    mockUserMe,
    mockPTeam: pteamData,
    mockTickets: ticketsData,
  } = config;

  // Get base handlers for vulnerability table
  const baseHandlers = createVulnerabilityTableHandlers(pteamId, serviceId, packageId);

  // Additional handlers specific to PackagePage
  const additionalHandlers = [
    // getPteam (override with provided mockPTeam)
    http.get(`*/pteams/${pteamId}`, () => {
      return HttpResponse.json(pteamData);
    }),

    // getDependencies (already in baseHandlers)

    // getVulnIds
    http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
      const url = new URL(request.url);
      if (url.searchParams.get("related_ticket_status") === "unsolved") {
        return HttpResponse.json(mockVulnIdsUnsolved);
      }
      if (url.searchParams.get("related_ticket_status") === "solved") {
        return HttpResponse.json(mockVulnIdsSolved);
      }
      return HttpResponse.json({ vuln_ids: [] });
    }),

    // getTicketCounts
    http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
      const url = new URL(request.url);
      if (url.searchParams.get("related_ticket_status") === "unsolved") {
        return HttpResponse.json(mockTicketCountsUnsolved);
      }
      if (url.searchParams.get("related_ticket_status") === "solved") {
        return HttpResponse.json(mockTicketCountsSolved);
      }
      return HttpResponse.json({
        ssvc_priority_count: { immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0 },
      });
    }),

    // getVuln (override to use mockVulnDetailsForPackagePage for PackagePage CVE IDs)
    http.get("*/vulns/:vulnId", ({ params }) => {
      const vulnId = params.vulnId;

      // Check mockVulnDetailsForPackagePage first (for CVE IDs used in PackagePage)
      const vulnDetail = mockVulnDetailsForPackagePage[vulnId];
      if (vulnDetail) {
        return HttpResponse.json(vulnDetail);
      }

      // Fall back to mockVulnDetails (for vuln-001, vuln-002, etc.)
      const fallbackDetail = mockVulnDetails[vulnId];
      if (fallbackDetail) {
        return HttpResponse.json(fallbackDetail);
      }

      return HttpResponse.json({ message: "Not Found" }, { status: 404 });
    }),

    // getVulnActions
    http.get("*/vulns/:vulnId/actions", ({ params }) => {
      const { vulnId } = params;
      const actionsData = mockVulnActions?.[vulnId];
      if (actionsData) {
        return HttpResponse.json(actionsData);
      }
      return HttpResponse.json([]);
    }),

    // getPteamTickets (override if ticketsData provided)
    http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
      const url = new URL(request.url);
      const vulnId = url.searchParams.get("vuln_id");
      const reqPackageId = url.searchParams.get("package_id");
      const reqServiceId = url.searchParams.get("service_id");

      if (
        ticketsData &&
        reqPackageId === packageId &&
        reqServiceId === serviceId &&
        ticketsData[vulnId]
      ) {
        return HttpResponse.json(ticketsData[vulnId]);
      }

      // Fall back to base handler logic
      if (vulnId === "vuln-001") {
        return HttpResponse.json([
          {
            ticket_id: "ticket-001",
            vuln_id: vulnId,
            dependency_id: "dep-1",
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: "immediate",
            ticket_safety_impact: "catastrophic",
            ticket_safety_impact_change_reason: "Critical vulnerability",
            ticket_status: {
              status_id: "status-001",
              ticket_handling_status: "alerted",
              user_id: "user-001",
              created_at: "2025-11-25T16:51:50.032Z",
              updated_at: "2025-11-25T16:51:50.032Z",
              assignees: [],
              note: "Initial alert - 未着手",
              scheduled_at: null,
              action_logs: [],
            },
          },
          {
            ticket_id: "ticket-002",
            vuln_id: vulnId,
            dependency_id: "dep-2",
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: "out_of_cycle",
            ticket_safety_impact: "major",
            ticket_safety_impact_change_reason: "Under investigation",
            ticket_status: {
              status_id: "status-002",
              ticket_handling_status: "acknowledged",
              user_id: "user-002",
              created_at: "2025-11-26T08:00:00.032Z",
              updated_at: "2025-11-26T09:00:00.032Z",
              assignees: ["user-003"],
              note: "Acknowledged - 対応中",
              scheduled_at: null,
              action_logs: [],
            },
          },
        ]);
      }

      return HttpResponse.json([]);
    }),

    // getMembers
    http.get(`*/pteams/${pteamId}/members`, () => {
      return HttpResponse.json(mockMembersList);
    }),

    // getUserMe
    http.get("*/users/me", () => {
      return HttpResponse.json(mockUserMe);
    }),
  ];

  // Return all handlers (additionalHandlers will override baseHandlers due to MSW's handler priority)
  return [...additionalHandlers, ...baseHandlers];
}
