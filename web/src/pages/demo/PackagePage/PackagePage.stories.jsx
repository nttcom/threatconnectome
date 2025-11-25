import { http, HttpResponse } from "msw";

import {
  mockVulnerabilities,
  mockMembers,
  mockPackageData,
  mockPackageReferences,
  mockDefaultSafetyImpact,
  mockSsvcCounts,
  mockTabCounts,
  mockPTeam,
  mockDependencies,
  mockVulnIdsUnsolved,
  mockVulnIdsSolved,
  mockVulnDetails,
} from "../mockData";

import PackagePage from "./PackagePage";

const pteamId = "pteam-abc-123";
const serviceId = "service-a";
const packageId = "pkg-uuid-456";

export default {
  title: "demo/PackagePage",
  component: PackagePage,
  parameters: {
    layout: "fullscreen",
  },
};

export const Default = {
  args: {
    packageData: mockPackageData,
    packageReferences: mockPackageReferences,
    defaultSafetyImpact: mockDefaultSafetyImpact,
    ssvcCounts: mockSsvcCounts,
    tabCounts: mockTabCounts,
    initialVulnerabilities: mockVulnerabilities,
    members: mockMembers,
    serviceId: serviceId,
  },
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}`, () => {
          return HttpResponse.json(mockPTeam);
        }),
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json(mockDependencies);
        }),
        http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
          const url = new URL(request.url);
          const status = url.searchParams.get("related_ticket_status");
          if (status === "unsolved") {
            return HttpResponse.json(mockVulnIdsUnsolved);
          } else if (status === "solved") {
            return HttpResponse.json(mockVulnIdsSolved);
          }
          return HttpResponse.json(mockVulnIdsUnsolved);
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
          const url = new URL(request.url);
          const status = url.searchParams.get("related_ticket_status");
          return HttpResponse.json({
            pteam_id: pteamId,
            service_id: serviceId,
            package_id: packageId,
            related_ticket_status: status || "unsolved",
            ssvc_priority_count: {
              immediate: 2,
              out_of_cycle: 3,
              scheduled: 5,
              defer: 1,
            },
          });
        }),
        http.get(`*/vulns/:vulnId`, ({ params }) => {
          const vulnId = params.vulnId;
          const vulnDetail = mockVulnDetails[vulnId];
          if (vulnDetail) {
            return HttpResponse.json(vulnDetail);
          }
          return HttpResponse.json(null, { status: 404 });
        }),
        http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
          const url = new URL(request.url);
          const vulnId = url.searchParams.get("vuln_id");

          // Note: In real API, tickets are filtered by vuln_ids from /vuln_ids endpoint
          // which already filters by related_ticket_status (solved/unsolved)
          // So we return all tickets for the vulnerability here

          // Mock: vuln-001 has 2 tickets (1 unsolved: alerted, 1 solved: completed)
          // Mock: vuln-002 has 1 ticket (1 solved: completed)
          // Mock: vuln-003 has 1 ticket (1 solved: completed)
          if (vulnId === "vuln-001") {
            return HttpResponse.json([
              {
                ticket_id: "ticket-001",
                vuln_id: vulnId,
                dependency_id: packageId,
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
                  note: "Initial alert",
                  scheduled_at: "2025-11-25T16:51:50.032Z",
                  action_logs: [],
                },
              },
              {
                ticket_id: "ticket-002",
                vuln_id: vulnId,
                dependency_id: packageId,
                service_id: serviceId,
                pteam_id: pteamId,
                ssvc_deployer_priority: "out_of_cycle",
                ticket_safety_impact: "major",
                ticket_safety_impact_change_reason: "Needs attention",
                ticket_status: {
                  status_id: "status-002",
                  ticket_handling_status: "completed",
                  user_id: "user-002",
                  created_at: "2025-11-26T10:00:00.032Z",
                  updated_at: "2025-11-26T10:00:00.032Z",
                  assignees: ["user-003"],
                  note: "Under investigation",
                  scheduled_at: null,
                  action_logs: [],
                },
              },
            ]);
          } else if (vulnId === "vuln-002") {
            return HttpResponse.json([
              {
                ticket_id: "ticket-003",
                vuln_id: vulnId,
                dependency_id: packageId,
                service_id: serviceId,
                pteam_id: pteamId,
                ssvc_deployer_priority: "scheduled",
                ticket_safety_impact: "minor",
                ticket_safety_impact_change_reason: "Low priority",
                ticket_status: {
                  status_id: "status-003",
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
                ticket_id: "ticket-004",
                vuln_id: vulnId,
                dependency_id: packageId,
                service_id: serviceId,
                pteam_id: pteamId,
                ssvc_deployer_priority: "defer",
                ticket_safety_impact: "negligible",
                ticket_safety_impact_change_reason: "Resolved",
                ticket_status: {
                  status_id: "status-004",
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

          return HttpResponse.json([]);
        }),
      ],
    },
    router: {
      memoryRouterProps: {
        initialEntries: [`/packages/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`],
      },
      path: "/packages/:packageId",
      useRoutes: true,
    },
  },
};

export const EmptyState = {
  args: {
    packageData: mockPackageData,
    packageReferences: [],
    defaultSafetyImpact: mockDefaultSafetyImpact,
    ssvcCounts: { immediate: 0, high: 0, medium: 0, low: 0 },
    tabCounts: { unsolved: 0, solved: 42 },
    initialVulnerabilities: [],
    members: mockMembers,
    serviceId: serviceId,
  },
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}`, () => {
          return HttpResponse.json(mockPTeam);
        }),
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json([]);
        }),
        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({
            pteam_id: pteamId,
            service_id: serviceId,
            package_id: packageId,
            related_ticket_status: "unsolved",
            vuln_ids: [],
          });
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
          const url = new URL(request.url);
          const status = url.searchParams.get("related_ticket_status");
          return HttpResponse.json({
            pteam_id: pteamId,
            service_id: serviceId,
            package_id: packageId,
            related_ticket_status: status || "unsolved",
            ssvc_priority_count: {
              immediate: 0,
              out_of_cycle: 0,
              scheduled: 0,
              defer: 0,
            },
          });
        }),
        http.get(`*/vulns/*`, () => {
          return HttpResponse.json(null, { status: 404 });
        }),
        http.get(`*/pteams/${pteamId}/tickets`, () => {
          return HttpResponse.json([]);
        }),
      ],
    },
    router: {
      memoryRouterProps: {
        initialEntries: [`/packages/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`],
      },
      path: "/packages/:packageId",
      useRoutes: true,
    },
  },
};

const manyVulnerabilities = [
  ...mockVulnerabilities,
  ...Array.from({ length: 15 }, (_, i) => ({
    id: `vuln-extra-${i}`,
    title: `Additional Vulnerability ${i + 1}`,
    highestSsvc: "medium",
    updated_at: "2025-09-01",
    affected_versions: ["1.0.0"],
    patched_versions: ["1.0.1"],
    cveId: `CVE-2025-EXTRA-${i}`,
    description: "This is a generated description for testing pagination.",
    mitigation: "Generated mitigation advice.",
    tasks: [],
  })),
];

export const WithPagination = {
  args: {
    packageData: mockPackageData,
    packageReferences: mockPackageReferences,
    defaultSafetyImpact: mockDefaultSafetyImpact,
    ssvcCounts: mockSsvcCounts,
    tabCounts: { unsolved: manyVulnerabilities.length, solved: 42 },
    initialVulnerabilities: manyVulnerabilities,
    members: mockMembers,
    serviceId: serviceId,
  },
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}`, () => {
          return HttpResponse.json(mockPTeam);
        }),
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json(mockDependencies);
        }),
        http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
          const url = new URL(request.url);
          const status = url.searchParams.get("related_ticket_status");
          if (status === "unsolved") {
            return HttpResponse.json({
              pteam_id: pteamId,
              service_id: serviceId,
              package_id: packageId,
              related_ticket_status: "unsolved",
              vuln_ids: manyVulnerabilities.map((v) => v.id),
            });
          } else if (status === "solved") {
            return HttpResponse.json(mockVulnIdsSolved);
          }
          return HttpResponse.json(mockVulnIdsUnsolved);
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
          const url = new URL(request.url);
          const status = url.searchParams.get("related_ticket_status");
          return HttpResponse.json({
            pteam_id: pteamId,
            service_id: serviceId,
            package_id: packageId,
            related_ticket_status: status || "unsolved",
            ssvc_priority_count: {
              immediate: 5,
              out_of_cycle: 8,
              scheduled: 10,
              defer: 3,
            },
          });
        }),
        http.get(`*/vulns/:vulnId`, ({ params }) => {
          const vulnId = params.vulnId;

          // Check if it's in mockVulnDetails
          if (mockVulnDetails[vulnId]) {
            return HttpResponse.json(mockVulnDetails[vulnId]);
          }

          // Generate extra vulnerabilities dynamically
          if (vulnId.startsWith("vuln-extra-")) {
            const index = parseInt(vulnId.split("-").pop());
            return HttpResponse.json({
              title: `Additional Vulnerability ${index + 1}`,
              cve_id: `CVE-2025-EXTRA-${index}`,
              detail: "This is a generated description for testing pagination.",
              exploitation: "poc",
              automatable: "no",
              cvss_v3_score: 5.0 + (index % 5),
              vulnerable_packages: [],
              vuln_id: vulnId,
              created_at: "2025-08-01T00:00:00Z",
              updated_at: "2025-09-01T00:00:00Z",
              created_by: "user-generated",
            });
          }

          return HttpResponse.json(null, { status: 404 });
        }),
        http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
          const url = new URL(request.url);
          const vulnId = url.searchParams.get("vuln_id");

          // Note: In real API, tickets are filtered by vuln_ids from /vuln_ids endpoint
          // which already filters by related_ticket_status (solved/unsolved)
          // So we return all tickets for the vulnerability here

          // Mock: Generate 1-3 tickets per vulnerability randomly
          // Mix of completed and non-completed tickets
          const numTickets = vulnId ? (vulnId.charCodeAt(vulnId.length - 1) % 3) + 1 : 0;
          const tickets = Array.from({ length: numTickets }, (_, i) => ({
            ticket_id: `ticket-${vulnId}-${i}`,
            vuln_id: vulnId,
            dependency_id: packageId,
            service_id: serviceId,
            pteam_id: pteamId,
            ssvc_deployer_priority: ["immediate", "out_of_cycle", "scheduled", "defer"][i % 4],
            ticket_safety_impact: ["catastrophic", "major", "minor", "negligible"][i % 4],
            ticket_safety_impact_change_reason: `Ticket ${i + 1} for ${vulnId}`,
            ticket_status: {
              status_id: `status-${vulnId}-${i}`,
              // Mix of completed and non-completed tickets
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
        }),
      ],
    },
    router: {
      memoryRouterProps: {
        initialEntries: [`/packages/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`],
      },
      path: "/packages/:packageId",
      useRoutes: true,
    },
  },
};
