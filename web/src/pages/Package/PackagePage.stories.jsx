import { http, HttpResponse } from "msw";

import { Package } from "./PackagePage";

const pteamId = "pteam-abc-123";
const serviceId = "service-xyz-789";
const packageId = "pkg-uuid-456";
const mockPTeam = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  services: [
    { service_id: serviceId, service_name: "My Production Service", service_safety_impact: "high" },
  ],
};
const mockDependencies = [
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
const mockVulnIdsUnsolved = {
  vuln_ids: ["CVE-2021-44228", "CVE-2022-1234"],
};
const mockVulnIdsSolved = {
  vuln_ids: ["CVE-2020-5678"],
};
const mockTicketCountsUnsolved = {
  ssvc_priority_count: {
    immediate: 1,
    out_of_cycle: 1,
    scheduled: 0,
    defer: 0,
  },
};
const mockTicketCountsSolved = {
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 0,
    scheduled: 1,
    defer: 0,
  },
};
const mockVulnDetails = {
  "CVE-2021-44228": {
    vuln_id: "CVE-2021-44228",
    title: "Log4Shell: RCE in Log4j",
    detail: "A remote code execution vulnerability...",
    cve_id: "CVE-2021-44228",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["2.0.0"],
        fixed_versions: ["2.17.1"],
      },
    ],
  },
  "CVE-2022-1234": {
    vuln_id: "CVE-2022-1234",
    title: "Another Vulnerability",
    cve_id: "CVE-2022-1234",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["1.0.0"],
        fixed_versions: ["1.1.0"],
      },
    ],
  },
  "CVE-2020-5678": {
    vuln_id: "CVE-2020-5678",
    title: "Solved Vulnerability",
    cve_id: "CVE-2020-5678",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["0.9.0"],
        fixed_versions: ["0.9.1"],
      },
    ],
  },
};
const mockVulnActions = {
  "CVE-2021-44228": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "CVE-2022-1234": [],
  "CVE-2020-5678": [],
};
const mockTickets = {
  "CVE-2021-44228": [
    {
      ticket_id: "ticket-1",
      dependency_id: "dep-1",
      ssvc_deployer_priority: "immediate",
      ticket_status: {
        ticket_handling_status: "acknowledged",
        scheduled_at: "2025-10-20T12:00:00Z",
        assignees: ["user-1"],
      },
    },
  ],
  "CVE-2022-1234": [
    {
      ticket_id: "ticket-2",
      dependency_id: "dep-1",
      ssvc_deployer_priority: "out_of_cycle",
      ticket_status: {
        ticket_handling_status: "alerted",
        scheduled_at: null,
        assignees: [],
      },
    },
  ],
  "CVE-2020-5678": [
    {
      ticket_id: "ticket-3",
      dependency_id: "dep-2",
      ssvc_deployer_priority: "scheduled",
      ticket_status: {
        ticket_handling_status: "completed",
        scheduled_at: "2025-01-01T00:00:00Z",
        assignees: ["user-1", "user-2"],
      },
    },
  ],
};
const mockMembersList = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
];

const mockUserMe = {
  user_id: "current-user-123",
  name: "Current User",
  email: "current.user@example.com",
  pteam_roles: [],
};

const successHandlers = [
  http.get(`*/pteams/${pteamId}`, () => {
    return HttpResponse.json(mockPTeam);
  }),
  http.get(`*/pteams/${pteamId}/dependencies`, ({ request }) => {
    const url = new URL(request.url);
    if (
      url.searchParams.get("service_id") === serviceId &&
      url.searchParams.get("package_id") === packageId
    ) {
      return HttpResponse.json(mockDependencies);
    }
  }),
  http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("related_ticket_status") === "unsolved") {
      return HttpResponse.json(mockVulnIdsUnsolved);
    }
    if (url.searchParams.get("related_ticket_status") === "solved") {
      return HttpResponse.json(mockVulnIdsSolved);
    }
  }),
  http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("related_ticket_status") === "unsolved") {
      return HttpResponse.json(mockTicketCountsUnsolved);
    }
    if (url.searchParams.get("related_ticket_status") === "solved") {
      return HttpResponse.json(mockTicketCountsSolved);
    }
  }),
  http.get("*/vulns/:vulnId", ({ params }) => {
    const { vulnId } = params;
    const vulnData = mockVulnDetails[vulnId];
    if (vulnData) {
      return HttpResponse.json(vulnData);
    }
    return HttpResponse.json({ message: "Not Found" }, { status: 404 });
  }),
  http.get("*/vulns/:vulnId/actions", ({ params }) => {
    const { vulnId } = params;
    const actionsData = mockVulnActions[vulnId];
    if (actionsData) {
      return HttpResponse.json(actionsData);
    }
    return HttpResponse.json([]);
  }),
  http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
    const url = new URL(request.url);
    const vulnId = url.searchParams.get("vuln_id");
    const reqPackageId = url.searchParams.get("package_id");
    const reqServiceId = url.searchParams.get("service_id");

    if (reqPackageId === packageId && reqServiceId === serviceId && mockTickets[vulnId]) {
      return HttpResponse.json(mockTickets[vulnId]);
    }
    return HttpResponse.json([]);
  }),
  http.get(`*/pteams/${pteamId}/members`, () => {
    return HttpResponse.json(mockMembersList);
  }),

  http.get("*/users/me", () => {
    return HttpResponse.json(mockUserMe);
  }),
];

export default {
  title: "Package/PackagePage",
  component: Package,
  tags: ["autodocs"],
};

export const Default = {
  parameters: {
    msw: {
      handlers: successHandlers,
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

export const Loading = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}`, async () => {
          await new Promise(() => {});
        }),
        successHandlers[1],
        successHandlers[2],
        successHandlers[3],
        successHandlers[4],
        successHandlers[5],
        successHandlers[6],
        successHandlers[7],
        successHandlers[8],
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

export const NoPTeamId = {
  parameters: {
    router: {
      memoryRouterProps: {
        initialEntries: [`/packages/${packageId}?serviceId=${serviceId}`],
      },
      path: "/packages/:packageId",
      useRoutes: true,
    },
  },
};

export const NoVulnerabilities = {
  parameters: {
    msw: {
      handlers: [
        successHandlers[0],
        successHandlers[1],

        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({ vuln_ids: [] });
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, () => {
          return HttpResponse.json({
            ssvc_priority_count: { immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0 },
          });
        }),

        successHandlers[4],
        successHandlers[5],
        successHandlers[6],
        successHandlers[7],
        successHandlers[8],
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
