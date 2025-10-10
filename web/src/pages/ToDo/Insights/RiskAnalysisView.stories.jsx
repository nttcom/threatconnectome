import emptyInsightData from "../../../mocks/emptyInsightData.json";
import generalInsightData from "../../../mocks/generalInsightData.json";

import { RiskAnalysisView } from "./RiskAnalysisView.jsx";

export default {
  title: "RiskAnalysis/RiskAnalysisView",
  component: RiskAnalysisView,
  args: {
    serviceName: "Example Service",
    ecosystem: "WebApp",
    cveId: "CVE-2025-XXXX",
    cvss: "9.8 CRITICAL",
  },
};

export const Default = {
  args: {
    insight: generalInsightData,
  },
};

export const EmptyState = {
  args: {
    insight: emptyInsightData,
  },
};
