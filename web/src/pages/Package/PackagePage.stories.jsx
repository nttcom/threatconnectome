import { http, HttpResponse } from "msw";

import { Package } from "./PackagePage";
import { pteamId, serviceId, packageId, createDefaultHandlers } from "./mocks/mockData";

const defaultHandlers = createDefaultHandlers();

export default {
  title: "PackagePage",
  component: Package,
  tags: ["autodocs"],
};

export const Default = {
  parameters: {
    msw: {
      handlers: defaultHandlers,
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
        ...defaultHandlers,
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
        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({ vuln_ids: [] });
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, () => {
          return HttpResponse.json({
            ssvc_priority_count: { immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0 },
          });
        }),
        ...defaultHandlers,
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

export const NoDependencies = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json([]);
        }),
        ...defaultHandlers,
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

export const DependenciesError = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json({ detail: "Failed to fetch dependencies" }, { status: 500 });
        }),
        ...defaultHandlers,
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

export const PTeamError = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}`, () => {
          return HttpResponse.json({ detail: "PTeam not found" }, { status: 404 });
        }),
        ...defaultHandlers,
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

export const NoServiceId = {
  parameters: {
    router: {
      memoryRouterProps: {
        initialEntries: [`/packages/${packageId}?pteamId=${pteamId}`],
      },
      path: "/packages/:packageId",
      useRoutes: true,
    },
  },
};

export const VulnIdsError = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({ detail: "Failed to fetch vuln_ids" }, { status: 500 });
        }),
        ...defaultHandlers,
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

export const TicketCountsError = {
  parameters: {
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/ticket_counts`, () => {
          return HttpResponse.json({ detail: "Failed to fetch ticket_counts" }, { status: 500 });
        }),
        ...defaultHandlers,
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
