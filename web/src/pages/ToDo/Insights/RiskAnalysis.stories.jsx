import { configureStore } from "@reduxjs/toolkit";
import { http, HttpResponse } from "msw";
import { Provider } from "react-redux";

import emptyInsightData from "../../../mocks/emptyInsightData.json";
import generalInsightData from "../../../mocks/generalInsightData.json";
import { tcApi } from "../../../services/tcApi";
import { sliceReducers } from "../../../slices";

import { RiskAnalysis } from "./RiskAnalysis.jsx";

const mockAuthedState = {
  auth: {
    authUserIsReady: true,
  },
};

const rootReducer = {
  ...sliceReducers,
  [tcApi.reducerPath]: tcApi.reducer,
};

export default {
  title: "RiskAnalysis",
  component: RiskAnalysis,

  decorators: [
    (Story) => {
      const mockStore = configureStore({
        reducer: rootReducer,
        preloadedState: mockAuthedState,
        middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
      });
      return (
        <Provider store={mockStore}>
          <Story />
        </Provider>
      );
    },
  ],

  args: {
    ticketId: "ticket-123",
    serviceName: "Example Service",
    ecosystem: "WebApp",
    cveId: "CVE-2025-XXXX",
    cvss: "9.8 CRITICAL",
  },
};

export const Default = {
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
