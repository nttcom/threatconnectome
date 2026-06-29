import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { useTranslation } from "react-i18next";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetInsightQuery } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { RiskAnalysisView } from "./RiskAnalysisView";

type RiskAnalysisProps = {
  ticketId: string;
  serviceName: string;
  ecosystem: string;
  cveId: string;
  cvss: string;
};

function isFetchBaseQueryError(error: unknown): error is FetchBaseQueryError {
  return typeof error === "object" && error !== null && "status" in error;
}

export function RiskAnalysis(props: RiskAnalysisProps) {
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
    if (isFetchBaseQueryError(insightError) && insightError.status === 404) {
      return <>{t("noInsight")}</>;
    }
    throw new APIError(errorToString(insightError), {
      api: "getInsight",
    });
  }
  if (insightIsLoading) return <>{t("loadingInsight")}</>;
  if (!insight) return <>{t("noInsight")}</>;

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
