import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth.js";
import { useGetInsightQuery } from "../../../services/tcApi.js";
import { APIError } from "../../../utils/APIError.js";
import { errorToString } from "../../../utils/func";

import { RiskAnalysisView } from "./RiskAnalysisView.jsx";

export function RiskAnalysis(props) {
  const { ticketId, serviceName, ecosystem, cveId, cvss } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "Insights.RiskAnalysis" });

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: insight,
    error: insightError,
    isLoading: insightIsLoading,
  } = useGetInsightQuery(
    {
      path: {
        ticket_id: ticketId,
      },
    },
    { skip },
  );

  if (skip) return <></>;
  if (insightError) {
    if (insightError.status === 404) {
      return <>{t("noInsight")}</>;
    }
    throw new APIError(errorToString(insightError), {
      api: "getInsight",
    });
  }
  if (insightIsLoading) return <>{t("loadingInsight")}</>;

  return (
    <RiskAnalysisView
      insight={insight}
      serviceName={serviceName}
      ecosystem={ecosystem}
      cveId={cveId}
      cvss={cvss}
    />
  );
}

RiskAnalysis.propTypes = {
  ticketId: PropTypes.string.isRequired,
  serviceName: PropTypes.string.isRequired,
  ecosystem: PropTypes.string.isRequired,
  cveId: PropTypes.string.isRequired,
  cvss: PropTypes.string.isRequired,
};
