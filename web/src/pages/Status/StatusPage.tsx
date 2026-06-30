import { Box } from "@mui/material";
import { useCallback, useEffect, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { PTeamLabel } from "../../components/PTeamLabel";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetPTeamQuery,
  useGetPTeamPackageVersionsSummaryQuery,
  useGetPTeamServiceThumbnailQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import {
  buildCurrentServiceFromPTeam,
  buildDependencyRows,
  buildServiceTabsFromPTeam,
} from "../../utils/SBOMManagement/sbomManagementUtils";
import { getNoPTeamMessage } from "../../utils/const";
import { errorToString } from "../../utils/func";
import { preserveMyTasksParam, preserveParams } from "../../utils/urlUtils";

import { SBOMManagement } from "./SBOMManagement/SBOMManagement";
import { SBOMUploadProgressButton } from "./SbomProgress/SBOMUploadProgressButton";
import type { PTeamInfo, PTeamServiceResponse } from "../../../types/types.gen";

function getValidServiceId(
  services: PTeamServiceResponse[],
  requestedServiceId: string | null,
): string | null {
  if (requestedServiceId && services.some((service) => service.service_id === requestedServiceId)) {
    return requestedServiceId;
  }

  return services[0]?.service_id ?? null;
}

export function Status() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const { t } = useTranslation("status", { keyPrefix: "StatusPage" });

  const {
    data: pteam,
    error: pteamError,
    isFetching: pteamIsFetching,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId ?? "" } }, { skip: skipByAuth || !pteamId });

  useEffect(() => {
    if (!pteamId) return;
    if (pteamIsFetching || !pteam || pteam.pteam_id !== pteamId) return;

    const validServiceId = getValidServiceId(pteam.services, serviceId);
    if (serviceId === validServiceId) {
      return;
    }

    const newParams = new URLSearchParams();
    newParams.set("pteamId", pteamId);
    if (validServiceId) {
      newParams.set("serviceId", validServiceId);
    }
    const mytasksParam = preserveMyTasksParam(location.search);
    for (const [key, value] of mytasksParam) {
      newParams.set(key, value);
    }
    navigate(location.pathname + "?" + newParams.toString());
  }, [location.pathname, location.search, navigate, pteam, pteamId, pteamIsFetching, serviceId]);

  if (!pteamId) return <>{getNoPTeamMessage()}</>;
  if (skipByAuth) return <></>;
  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamIsLoading) return <>{t("loading_team")}</>;
  if (!pteam || pteam.pteam_id !== pteamId) return <>{t("loading_team")}</>;

  const validServiceId = getValidServiceId(pteam.services, serviceId);
  if (serviceId !== validServiceId) return <></>;
  if (!validServiceId) return <StatusEmptyBody pteamId={pteamId} />;

  return <StatusBody pteamId={pteamId} pteam={pteam} serviceId={validServiceId} />;
}

function StatusHeader({ pteamId }: { pteamId: string }) {
  return (
    <>
      <Box display="flex" flexDirection="row">
        <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
        <SBOMUploadProgressButton pteamId={pteamId} />
      </Box>
    </>
  );
}

function StatusEmptyBody({ pteamId }: { pteamId: string }) {
  return (
    <>
      <StatusHeader pteamId={pteamId} />
      <SBOMManagement
        currentDependencies={[]}
        currentService={null}
        pteamId={pteamId}
        serviceTabs={[]}
      />
    </>
  );
}

function StatusBody({
  pteamId,
  pteam,
  serviceId,
}: {
  pteamId: string;
  pteam: PTeamInfo;
  serviceId: string;
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const skipByAuth = useSkipUntilAuthUserIsReady();

  const { currentData: packageVersionsSummary, error: packageVersionsSummaryError } =
    useGetPTeamPackageVersionsSummaryQuery(
      { path: { pteam_id: pteamId }, query: { service_id: serviceId } },
      { skip: skipByAuth || !pteamId },
    );

  const { data: loadedThumbnail, error: loadedThumbnailError } = useGetPTeamServiceThumbnailQuery(
    { path: { pteam_id: pteamId, service_id: serviceId } },
    { skip: skipByAuth || !pteamId },
  );

  if (packageVersionsSummaryError)
    throw new APIError(errorToString(packageVersionsSummaryError), {
      api: "getPTeamPackageVersionsSummary",
    });

  const serviceTabs = useMemo(() => buildServiceTabsFromPTeam(pteam.services), [pteam.services]);

  const normalizedThumbnail =
    loadedThumbnailError && "status" in loadedThumbnailError && loadedThumbnailError.status === 404
      ? ""
      : ((loadedThumbnail as string | undefined) ?? "");

  const currentService = useMemo(
    () => buildCurrentServiceFromPTeam(pteam.services, serviceId, normalizedThumbnail),
    [normalizedThumbnail, pteam.services, serviceId],
  );

  const currentDependencies = useMemo(
    () => buildDependencyRows(packageVersionsSummary?.package_versions ?? [], serviceId),
    [packageVersionsSummary, serviceId],
  );

  const handleActiveIdChange = useCallback(
    (serviceId: string) => {
      const newParams = new URLSearchParams(location.search);
      newParams.set("serviceId", serviceId);
      navigate(location.pathname + "?" + newParams.toString());
    },
    [location, navigate],
  );

  const handlePackageClick = useCallback(
    (serviceId: string, packageVersionId: string) => {
      const preservedParams = preserveParams(location.search);
      preservedParams.set("pteamId", pteamId);
      preservedParams.set("serviceId", serviceId);
      navigate(`/package_versions/${packageVersionId}?${preservedParams.toString()}`);
    },
    [location.search, navigate, pteamId],
  );

  return (
    <>
      <StatusHeader pteamId={pteamId} />
      <SBOMManagement
        currentDependencies={currentDependencies}
        currentService={currentService}
        onActiveIdChange={handleActiveIdChange}
        onPackageClick={handlePackageClick}
        pteamId={pteamId}
        serviceTabs={serviceTabs}
      />
    </>
  );
}
