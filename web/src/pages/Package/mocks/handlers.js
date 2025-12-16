import { http, HttpResponse, delay } from "msw";

import {
  pteamId,
  serviceId,
  mockPTeam,
  mockUserMe,
  mockVulnIdsSolved,
  mockVulnIdsUnsolved,
  mockTicketCountsSolved,
  mockTicketCountsUnsolved,
  mockDependencies,
  mockVulnDetails,
  mockVulnActions,
  mockMembersList,
  mockTicketsVuln001,
  mockTicketsVuln002,
  mockTicketsVuln003,
} from "./mockData";

// Delay setting (ms) - set to 0 to disable delay
const MOCK_DELAY = 500;

// === MSW Handler Factory ===
/**
 * Create common default handlers for PackagePage and VulnerabilityTable
 */
export function createDefaultHandlers() {
  return [
    // getPTeam
    http.get(`*/pteams/${pteamId}`, async () => {
      await delay(MOCK_DELAY);
      return HttpResponse.json(mockPTeam);
    }),
    // getUserMe
    http.get("http://localhost:8000/api/users/me", async () => {
      await delay(MOCK_DELAY);
      return HttpResponse.json(mockUserMe, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
    http.get("*/users/me", async () => {
      await delay(MOCK_DELAY);
      return HttpResponse.json(mockUserMe, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
    // getVulnIds
    http.get(`*/pteams/${pteamId}/vuln_ids`, async ({ request }) => {
      await delay(MOCK_DELAY);
      const url = new URL(request.url);
      const relatedTicketStatus = url.searchParams.get("related_ticket_status");
      if (relatedTicketStatus === "solved") {
        return HttpResponse.json(mockVulnIdsSolved);
      }
      return HttpResponse.json(mockVulnIdsUnsolved);
    }),
    // getTicketCounts
    http.get(`*/pteams/${pteamId}/ticket_counts`, async ({ request }) => {
      await delay(MOCK_DELAY);
      const url = new URL(request.url);
      const relatedTicketStatus = url.searchParams.get("related_ticket_status");
      if (relatedTicketStatus === "solved") {
        return HttpResponse.json(mockTicketCountsSolved);
      }
      return HttpResponse.json(mockTicketCountsUnsolved);
    }),
    // getDependencies
    http.get(`*/pteams/${pteamId}/dependencies`, async () => {
      await delay(MOCK_DELAY);
      return HttpResponse.json(mockDependencies);
    }),
    // getDependency
    http.get(`*/pteams/${pteamId}/dependencies/:dependencyId`, async ({ params }) => {
      await delay(MOCK_DELAY);
      const { dependencyId } = params;
      const dependency = mockDependencies.find((dep) => dep.dependency_id === dependencyId);
      if (dependency) {
        return HttpResponse.json(dependency);
      }
      return HttpResponse.json({ detail: "No such dependency" }, { status: 404 });
    }),
    // getVuln
    http.get("*/vulns/:vulnId", async ({ params }) => {
      await delay(MOCK_DELAY);
      const vulnId = params.vulnId;
      const vulnDetail = mockVulnDetails[vulnId];
      if (vulnDetail) {
        return HttpResponse.json(vulnDetail);
      }
      // Dynamic generation for pagination testing
      if (vulnId.startsWith("vuln-extra-")) {
        const index = parseInt(vulnId.split("-").pop());
        return HttpResponse.json({
          vuln_id: vulnId,
          title: `Additional Vulnerability ${index + 1}`,
          cve_id: `CVE-2025-EXTRA-${index}`,
          detail: "This is a generated description for testing pagination.",
          exploitation: "poc",
          automatable: "no",
          cvss_v3_score: 5.0 + (index % 5),
          vulnerable_packages: [
            {
              affected_name: "example-package",
              ecosystem: "npm",
              affected_versions: ["1.0.0"],
              fixed_versions: ["1.1.0"],
            },
          ],
          created_at: "2025-08-01T00:00:00Z",
          updated_at: "2025-09-01T00:00:00Z",
          created_by: "user-generated",
        });
      }
      return HttpResponse.json(null, { status: 404 });
    }),
    // getVulnActions
    http.get("*/vulns/:vulnId/actions", async ({ params }) => {
      await delay(MOCK_DELAY);
      const { vulnId } = params;
      const actionsData = mockVulnActions?.[vulnId];
      if (actionsData) {
        return HttpResponse.json(actionsData);
      }
      return HttpResponse.json([]);
    }),
    // getPteamTickets
    http.get(`*/pteams/${pteamId}/tickets`, async ({ request }) => {
      await delay(MOCK_DELAY);
      const url = new URL(request.url);
      const vulnId = url.searchParams.get("vuln_id");
      if (vulnId === "vuln-001") {
        return HttpResponse.json(mockTicketsVuln001);
      } else if (vulnId === "vuln-002") {
        return HttpResponse.json(mockTicketsVuln002);
      } else if (vulnId === "vuln-003") {
        return HttpResponse.json(mockTicketsVuln003);
      }
      // Dynamic generation for pagination testing
      if (vulnId && vulnId.startsWith("vuln-extra-")) {
        const numTickets = (vulnId.charCodeAt(vulnId.length - 1) % 3) + 1;
        const tickets = Array.from({ length: numTickets }, (_, i) => ({
          ticket_id: `ticket-${vulnId}-${i}`,
          vuln_id: vulnId,
          dependency_id: i % 2 === 0 ? "dep-1" : "dep-2",
          service_id: serviceId,
          pteam_id: pteamId,
          ssvc_deployer_priority: ["immediate", "out_of_cycle", "scheduled", "defer"][i % 4],
          ticket_safety_impact: ["catastrophic", "major", "minor", "negligible"][i % 4],
          ticket_safety_impact_change_reason: `Ticket ${i + 1} for ${vulnId}`,
          ticket_status: {
            status_id: `status-${vulnId}-${i}`,
            ticket_handling_status:
              i % 2 === 0 ? "completed" : ["alerted", "acknowledged", "scheduled"][i % 3],
            user_id: `user-${i % 3}`,
            created_at: "2025-11-25T16:51:50.032Z",
            updated_at: "2025-11-25T16:51:50.032Z",
            assignees: i === 0 ? ["user-001"] : [],
            note: `Mock ticket ${i + 1}`,
            scheduled_at: i === 2 ? "2025-12-01T00:00:00.032Z" : null,
            action_logs: [],
          },
        }));
        return HttpResponse.json(tickets);
      }
      return HttpResponse.json([]);
    }),
    // getPTeamMembers
    http.get(`*/pteams/${pteamId}/members`, async () => {
      await delay(MOCK_DELAY);
      return HttpResponse.json(mockMembersList);
    }),

    // ========================================
    // Mutation Handlers
    // ========================================

    // updateTicket - Update ticket
    http.put(`*/pteams/${pteamId}/tickets/:ticketId`, async ({ request, params }) => {
      await delay(MOCK_DELAY);
      const { ticketId } = params;
      const body = await request.json();

      // Find existing ticket data
      const allTickets = [...mockTicketsVuln001, ...mockTicketsVuln002, ...mockTicketsVuln003];
      const existingTicket = allTickets.find((t) => t.ticket_id === ticketId);

      if (!existingTicket) {
        return HttpResponse.json({ detail: "Ticket not found" }, { status: 404 });
      }

      // Return success response (merge request body content)
      const updatedTicket = {
        ...existingTicket,
        ...body,
        ticket_status: {
          ...existingTicket.ticket_status,
          ...(body.ticket_status || {}),
          updated_at: new Date().toISOString(),
        },
      };

      return HttpResponse.json(updatedTicket);
    }),

    // createActionLog - Create action log
    http.post(`*/actionlogs`, async ({ request }) => {
      await delay(MOCK_DELAY);
      const body = await request.json();

      // Return success response
      const actionLog = {
        logging_id: `log-${Date.now()}`,
        action: body.action,
        pteam_id: body.pteam_id || body.pteamId,
        service_id: body.service_id || body.serviceId,
        ticket_id: body.ticket_id || body.ticketId,
        vuln_id: body.vuln_id || body.vulnId,
        user_id: body.user_id || body.userId,
        created_at: new Date().toISOString(),
      };

      return HttpResponse.json(actionLog);
    }),
  ];
}
