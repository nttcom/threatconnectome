import { http, HttpResponse } from "msw";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { ServiceEolDashboard } from "./ServiceEolDashboardPage";
import {
  MOCK_SERVICES_EXPIRED_ONLY,
  MOCK_SERVICES_DEADLINE_APPROACHING,
  MOCK_SERVICES_SUPPORTED_ONLY,
  MOCK_SERVICES_EMPTY,
  MOCK_SERVICES_DEFAULT,
} from "./mocks/serviceData";

const pteamId = "pteam-abc-123";

const meta = {
  title: "Eol/ServiceEolDashboard",
  component: ServiceEolDashboard,
  parameters: {
    layout: "fullscreen",
    router: {
      memoryRouterProps: {
        initialEntries: [`/eol?pteamId=${pteamId}`],
      },
      path: "/eol",
      useRoutes: true,
    },
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ServiceEolDashboard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/pteams/:pteamId/eols", () => {
          return HttpResponse.json(MOCK_SERVICES_DEFAULT);
        }),
      ],
    },
  },
};

export const ExpiredOnly: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/pteams/:pteamId/eols", () => {
          return HttpResponse.json(MOCK_SERVICES_EXPIRED_ONLY);
        }),
      ],
    },
  },
};

export const DeadlineApproachingOnly: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/pteams/:pteamId/eols", () => {
          return HttpResponse.json(MOCK_SERVICES_DEADLINE_APPROACHING);
        }),
      ],
    },
  },
};

export const SupportedOnly: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/pteams/:pteamId/eols", () => {
          return HttpResponse.json(MOCK_SERVICES_SUPPORTED_ONLY);
        }),
      ],
    },
  },
};

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/pteams/:pteamId/eols", () => {
          return HttpResponse.json(MOCK_SERVICES_EMPTY);
        }),
      ],
    },
  },
};
