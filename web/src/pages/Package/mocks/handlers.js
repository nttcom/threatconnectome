import { http, HttpResponse } from "msw";

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
// === MSW ハンドラーファクトリ ===
/**
 * PackagePageとVulnerabilityTableで共通のデフォルトハンドラーを作成
 */
export function createDefaultHandlers() {
  return [
    // getPTeam
    http.get(`*/pteams/${pteamId}`, () => {
      return HttpResponse.json(mockPTeam);
    }),
    // getUserMe
    http.get("http://localhost:8000/api/users/me", () => {
      return HttpResponse.json(mockUserMe, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
    http.get("*/users/me", () => {
      return HttpResponse.json(mockUserMe, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
    // getVulnIds
    http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
      const url = new URL(request.url);
      const relatedTicketStatus = url.searchParams.get("related_ticket_status");
      if (relatedTicketStatus === "solved") {
        return HttpResponse.json(mockVulnIdsSolved);
      }
      return HttpResponse.json(mockVulnIdsUnsolved);
    }),
    // getTicketCounts
    http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
      const url = new URL(request.url);
      const relatedTicketStatus = url.searchParams.get("related_ticket_status");
      if (relatedTicketStatus === "solved") {
        return HttpResponse.json(mockTicketCountsSolved);
      }
      return HttpResponse.json(mockTicketCountsUnsolved);
    }),
    // getDependencies
    http.get(`*/pteams/${pteamId}/dependencies`, () => {
      return HttpResponse.json(mockDependencies);
    }),
    // getDependency
    http.get(`*/pteams/${pteamId}/dependencies/:dependencyId`, ({ params }) => {
      const { dependencyId } = params;
      const dependency = mockDependencies.find((dep) => dep.dependency_id === dependencyId);
      if (dependency) {
        return HttpResponse.json(dependency);
      }
      return HttpResponse.json({ detail: "No such dependency" }, { status: 404 });
    }),
    // getVuln
    http.get("*/vulns/:vulnId", ({ params }) => {
      const vulnId = params.vulnId;
      const vulnDetail = mockVulnDetails[vulnId];
      if (vulnDetail) {
        return HttpResponse.json(vulnDetail);
      }
      // pagination testing用の動的生成
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
    http.get("*/vulns/:vulnId/actions", ({ params }) => {
      const { vulnId } = params;
      const actionsData = mockVulnActions?.[vulnId];
      if (actionsData) {
        return HttpResponse.json(actionsData);
      }
      return HttpResponse.json([]);
    }),
    // getPteamTickets
    http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
      const url = new URL(request.url);
      const vulnId = url.searchParams.get("vuln_id");
      if (vulnId === "vuln-001") {
        return HttpResponse.json(mockTicketsVuln001);
      } else if (vulnId === "vuln-002") {
        return HttpResponse.json(mockTicketsVuln002);
      } else if (vulnId === "vuln-003") {
        return HttpResponse.json(mockTicketsVuln003);
      }
      // pagination testing用の動的生成
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
    http.get(`*/pteams/${pteamId}/members`, () => {
      return HttpResponse.json(mockMembersList);
    }),

    // ========================================
    // Mutation ハンドラー
    // ========================================

    // updateTicket - チケット更新
    http.put(`*/pteams/${pteamId}/tickets/:ticketId`, async ({ request, params }) => {
      const { ticketId } = params;
      const body = await request.json();

      // 既存のチケットデータを探す
      const allTickets = [...mockTicketsVuln001, ...mockTicketsVuln002, ...mockTicketsVuln003];
      const existingTicket = allTickets.find((t) => t.ticket_id === ticketId);

      if (!existingTicket) {
        return HttpResponse.json({ detail: "Ticket not found" }, { status: 404 });
      }

      // 成功レスポンスを返す（リクエストボディの内容をマージ）
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
  ];
}
