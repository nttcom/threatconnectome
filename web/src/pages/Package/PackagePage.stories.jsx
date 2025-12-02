import { http, HttpResponse } from "msw";

import { Package } from "./PackagePage";
import { mockTickets } from "./VulnerabilityTable/mocks/mockData";
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
  createPackagePageHandlers,
} from "./mocks/mockData";

const successHandlers = createPackagePageHandlers({
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
  mockPTeam,
  mockTickets,
});

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
          await new Promise(() => {}); // Never resolves
        }),
        ...successHandlers.slice(1), // Use all other handlers from successHandlers
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
        // Override vuln_ids and ticket_counts to return empty
        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({ vuln_ids: [] });
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, () => {
          return HttpResponse.json({
            ssvc_priority_count: { immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0 },
          });
        }),
        // Include other success handlers
        ...successHandlers,
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
