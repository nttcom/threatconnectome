import { useParams } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { getUpdateActions } from "../../utils/vulnUtils";

import { VulnDetailView } from "./VulnDetailView";

export function VulnDetail() {
  const { vulnId } = useParams();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery({ path: { vuln_id: vulnId } }, { skip });

  if (skip) return <></>;
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return <>Now loading Vuln...</>;

  const updateActions = getUpdateActions(vuln);

  return <VulnDetailView vuln={vuln} updateActions={updateActions} />;
}
