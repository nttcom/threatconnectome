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

// const Template = (args) => <PackagePage {...args} />;

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
