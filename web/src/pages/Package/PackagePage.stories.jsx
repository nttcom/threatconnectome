import { http, HttpResponse } from "msw";

import { Package } from "./PackagePage";
import {
  mockDependencies,
  mockVulnDetailsForPackagePage,
  mockTickets,
} from "./VulnerabilityTable/mocks/mockData";
import {
  pteamId,
  serviceId,
  packageId,
  mockPTeam,
  mockVulnIdsUnsolved,
  mockVulnIdsSolved,
  mockTicketCountsUnsolved,
  mockTicketCountsSolved,
  mockVulnActions,
  mockMembersList,
  mockUserMe,
} from "./mocks/mockData";

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
    const vulnData = mockVulnDetailsForPackagePage[vulnId];
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
  title: "PackagePage",
  component: Package,
  tags: ["autodocs"],
  argTypes: {
    useSplitView: {
      control: "boolean",
      description: "Use new split-view table instead of legacy table",
      defaultValue: false,
    },
  },
};

export const Default = {
  args: {
    useSplitView: false,
  },
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

export const WithSplitView = {
  args: {
    useSplitView: true,
  },
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
