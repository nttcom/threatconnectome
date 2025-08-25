import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth.js";
import { useGetInsightQuery } from "../../../services/tcApi.js";
import { APIError } from "../../../utils/APIError.js";
import { errorToString } from "../../../utils/func.js";

import { AIRiskAnalysisView } from "./AIRiskAnalysisView.jsx";

export function AIRiskAnalysis(props) {
  const { ticketId, serviceName, ecosystem, cveId, cvss } = props;

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: insight,
    error: insightError,
    isLoading: insightIsLoading,
  } = useGetInsightQuery(ticketId, { skip });

  if (skip) return <></>;
  if (insightError) {
    if (insightError.status === 404) {
      return <>No insight</>;
    }
    throw new APIError(errorToString(insightError), {
      api: "getInsight",
    });
  }
  if (insightIsLoading) return <>Now loading Insight...</>;

  return (
    <AIRiskAnalysisView
      insight={insight}
      serviceName={serviceName}
      ecosystem={ecosystem}
      cveId={cveId}
      cvss={cvss}
    />
  );
}

AIRiskAnalysis.propTypes = {
  ticketId: PropTypes.string.isRequired,
  serviceName: PropTypes.string.isRequired,
  ecosystem: PropTypes.string.isRequired,
  cveId: PropTypes.string.isRequired,
  cvss: PropTypes.number.isRequired,
};
