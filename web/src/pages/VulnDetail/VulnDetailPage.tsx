import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnQuery } from "../../services/tcApi";
import type { VulnResponse } from "../../../types/types.gen";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { getUpdateActions } from "../../utils/vulnUtils";

import { VulnDetailView } from "./VulnDetailView";

export function VulnDetail() {
  const { vulnId = "" } = useParams();
  const { t } = useTranslation("vulnDetail", { keyPrefix: "VulnDetailPage" });

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery({ path: { vuln_id: vulnId } }, { skip });

  if (skip) return <></>;
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return <>{t("loadingVuln")}</>;

  const vulnResponse = vuln as VulnResponse;
  const updateActions = getUpdateActions(vulnResponse);

  return <VulnDetailView vuln={vulnResponse} updateActions={updateActions} />;
}
