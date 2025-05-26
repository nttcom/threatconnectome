import { useParams } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnActionsQuery, useGetVulnQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { getActions } from "../../utils/vulnUtils";

import { VulnDetailView } from "./VulnDetailView";

export function VulnDetail() {
  const { vulnId } = useParams();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery(vulnId, { skip });

  const {
    data: vulnActions,
    error: vulnActionsError,
    isLoading: vulnActionsIsLoading,
  } = useGetVulnActionsQuery(vulnId, { skip });

  if (skip) return <></>;
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return <>Now loading Vuln...</>;
  if (vulnActionsError)
    throw new APIError(errorToString(vulnActionsError), { api: "getVulnActions" });
  if (vulnActionsIsLoading) return <>Now loading vulnActions...</>;

  const actions = getActions(vuln, vulnActions);

  return <VulnDetailView vuln={vuln} actions={actions} />;
}
