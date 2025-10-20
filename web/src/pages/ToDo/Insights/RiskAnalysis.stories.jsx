import { http, HttpResponse } from "msw";

import emptyInsightData from "../../../mocks/emptyInsightData.json";
import generalInsightData from "../../../mocks/generalInsightData.json";

import { RiskAnalysis } from "./RiskAnalysis.jsx";

export default {
  title: "RiskAnalysis",
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
};

export const Default = {};

export const EmptyState = {
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

export const NotFoundError = {
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
