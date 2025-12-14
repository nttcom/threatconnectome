import { http, HttpResponse } from "msw";
// === 共通ID定数 ===
export const pteamId = "pteam-abc-123";
export const serviceId = "service-xyz-789";
export const packageId = "pkg-uuid-456";
// === 共通モックデータ ===
export const mockPTeam = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  services: [
    {
      service_id: serviceId,
      service_name: "My Production Service",
      service_safety_impact: "high",
    },
  ],
};
export const mockDependencies = [
  {
    dependency_id: "dep-1",
    target: "pom.xml",
    package_version: "1.2.3",
    package_name: "log4j",
    package_source_name: "org.apache.logging:log4j-core",
    package_manager: "maven",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-2",
    target: "another.xml",
    package_version: "1.2.3",
    package_name: "log4j",
    package_source_name: "org.apache.logging:log4j-core",
    package_manager: "maven",
    package_ecosystem: "maven",
  },
];
export const mockVulnIdsUnsolved = {
  vuln_ids: ["vuln-001", "vuln-002"],
};
export const mockVulnIdsSolved = {
  vuln_ids: ["vuln-003"],
};
export const mockTicketCountsUnsolved = {
  ssvc_priority_count: {
    immediate: 2,
    out_of_cycle: 3,
    scheduled: 5,
    defer: 1,
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
export const mockVulnDetails = {
  "vuln-001": {
    vuln_id: "vuln-001",
    title: "setuptools: Path Traversal Vulnerability",
    cve_id: "CVE-2023-12345",
    detail:
      "A path traversal vulnerability in setuptools allows an attacker to access arbitrary files on the filesystem by crafting a malicious package.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 7.5,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j",
        affected_versions: ["1.2.0", "1.1.9"],
        fixed_versions: ["1.2.1"],
      },
    ],
    created_at: "2025-10-01T00:00:00Z",
    updated_at: "2025-10-21T00:00:00Z",
    created_by: "user-001",
  },
  "vuln-002": {
    vuln_id: "vuln-002",
    title: "pypa/setuptools: Remote code execution",
    cve_id: "CVE-2022-54321",
    detail:
      "A critical RCE vulnerability exists in the pypa/setuptools library, allowing unauthenticated attackers to execute arbitrary code.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 9.8,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j",
        affected_versions: ["2.0.0", "1.9.9"],
        fixed_versions: ["2.1.0"],
      },
    ],
    created_at: "2025-09-15T00:00:00Z",
    updated_at: "2025-10-20T00:00:00Z",
    created_by: "user-002",
  },
  "vuln-003": {
    vuln_id: "vuln-003",
    title: "Log4j: Remote Code Execution (Log4Shell)",
    cve_id: "CVE-2021-44228",
    detail:
      "Apache Log4j2 <=2.14.1 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 10.0,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j",
        affected_versions: ["2.14.1", "2.14.0"],
        fixed_versions: ["2.15.0", "2.16.0"],
      },
    ],
    created_at: "2025-08-01T00:00:00Z",
    updated_at: "2025-10-19T00:00:00Z",
    created_by: "user-003",
  },
};
export const mockVulnActions = {
  "vuln-001": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "vuln-002": [],
  "vuln-003": [],
};
export const mockMembersList = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
  { user_id: "user-003", name: "Charlie", email: "charlie@example.com" },
];
export const mockUserMe = {
  user_id: "current-user-123",
  uid: "current-user",
  name: "Current User",
  email: "current.user@example.com",
  disabled: false,
  years: 5,
  pteam_roles: [],
};
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
              current_safety_impact: "catastrophic",
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
              current_safety_impact: "critical",
            },
          },
          {
            ticket_id: "ticket-003",
            vuln_id: vulnId,
            dependency_id: "dep-1",
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: "scheduled",
            ticket_safety_impact: null,
            ticket_safety_impact_change_reason: null,
            ticket_status: {
              status_id: "status-003",
              ticket_handling_status: "alerted",
              user_id: "user-001",
              created_at: "2025-11-27T10:00:00.032Z",
              updated_at: "2025-11-27T10:00:00.032Z",
              assignees: [],
              note: "Using default safety impact",
              scheduled_at: null,
              action_logs: [],
              current_safety_impact: null,
            },
          },
        ]);
      } else if (vulnId === "vuln-002") {
        return HttpResponse.json([
          {
            ticket_id: "ticket-005",
            vuln_id: vulnId,
            dependency_id: "dep-1",
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: "scheduled",
            ticket_safety_impact: "minor",
            ticket_safety_impact_change_reason: "Low priority",
            ticket_status: {
              status_id: "status-005",
              ticket_handling_status: "completed",
              user_id: "user-001",
              created_at: "2025-11-20T08:00:00.032Z",
              updated_at: "2025-11-20T08:00:00.032Z",
              assignees: [],
              note: "Scheduled for next sprint",
              scheduled_at: "2025-12-01T00:00:00.032Z",
              action_logs: [],
            },
          },
        ]);
      } else if (vulnId === "vuln-003") {
        return HttpResponse.json([
          {
            ticket_id: "ticket-006",
            vuln_id: vulnId,
            dependency_id: "dep-2",
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: "defer",
            ticket_safety_impact: "negligible",
            ticket_safety_impact_change_reason: "Resolved",
            ticket_status: {
              status_id: "status-006",
              ticket_handling_status: "completed",
              user_id: "user-001",
              created_at: "2025-11-18T08:00:00.032Z",
              updated_at: "2025-11-24T08:00:00.032Z",
              assignees: [],
              note: "Completed",
              scheduled_at: null,
              action_logs: [],
            },
          },
        ]);
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
  ];
}
