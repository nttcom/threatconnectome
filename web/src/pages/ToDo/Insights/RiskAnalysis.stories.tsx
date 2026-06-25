import type { Meta, StoryObj } from "@storybook/react";
import { http, HttpResponse } from "msw";

import emptyInsightData from "../../../mocks/emptyInsightData.json";
import generalInsightData from "../../../mocks/generalInsightData.json";

import { RiskAnalysis } from "./RiskAnalysis";

const meta = {
  component: RiskAnalysis,
  args: {
    ticketId: "ticket-123",
    serviceName: "Example Service",
    ecosystem: "WebApp",
    cveId: "CVE-2025-XXXX",
    cvss: "9.8 CRITICAL",
  },
  parameters: {
    msw: {
      handlers: [
        http.get("*/tickets/:ticketId/insight", () => {
          return HttpResponse.json(generalInsightData);
        }),
      ],
    },
  },
} satisfies Meta<typeof RiskAnalysis>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const EmptyState: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/tickets/:ticketId/insight", () => {
          return HttpResponse.json(emptyInsightData);
        }),
      ],
    },
  },
};

export const NotFoundError: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get("*/tickets/:ticketId/insight", () => {
          return new HttpResponse(null, { status: 404 });
        }),
      ],
    },
  },
};
