import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { PTeamLabel } from "../../components/PTeamLabel";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetPTeamQuery,
  useGetPTeamPackagesSummaryQuery,
  useGetPTeamServiceThumbnailQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { getNoPTeamMessage } from "../../utils/const";
import { errorToString } from "../../utils/func";
import { buildSbomsFromPTeam } from "../../utils/SBOMManagement/sbomManagementUtils";
import { preserveMyTasksParam, preserveParams } from "../../utils/urlUtils";

import { SBOMManagement } from "./SBOMManagement/SBOMManagement";
import { SBOMUploadProgressButton } from "./SbomProgress/SBOMUploadProgressButton";

function getValidServiceId(services, requestedServiceId) {
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
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip: skipByAuth || !pteamId });

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

  return <StatusBody pteamId={pteamId} pteam={pteam} serviceId={validServiceId} />;
}

function StatusBody({ pteamId, pteam, serviceId }) {
  const location = useLocation();
  const navigate = useNavigate();
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const [thumbnail, setThumbnail] = useState(null);

  const { currentData: packagesSummary, error: packagesSummaryError } =
    useGetPTeamPackagesSummaryQuery(
      { path: { pteam_id: pteamId }, query: { service_id: serviceId } },
      { skip: skipByAuth || !pteamId || !serviceId },
    );

  const { data: loadedThumbnail } = useGetPTeamServiceThumbnailQuery(
    { path: { pteam_id: pteamId, service_id: serviceId } },
    { skip: skipByAuth || !pteamId || !serviceId },
  );

  if (packagesSummaryError)
    throw new APIError(errorToString(packagesSummaryError), { api: "getPTeamPackagesSummary" });

  useEffect(() => {
    setThumbnail(null);
  }, [serviceId]);

  useEffect(() => {
    if (typeof loadedThumbnail === "string") {
      setThumbnail(loadedThumbnail);
    }
  }, [loadedThumbnail]);

  const handleThumbnailChanged = useCallback(
    (id, dataUrl) => {
      if (id !== serviceId) return;
      setThumbnail(dataUrl);
    },
    [serviceId],
  );

  const sboms = useMemo(() => {
    const base = buildSbomsFromPTeam(pteam.services, packagesSummary?.packages ?? [], serviceId);
    return base.map((sbom) => {
      if (sbom.id !== serviceId) return sbom;
      return { ...sbom, imageUrl: thumbnail ?? "" };
    });
  }, [pteam.services, packagesSummary, serviceId, thumbnail]);

  const handleActiveIdChange = useCallback(
    (serviceId) => {
      const newParams = new URLSearchParams(location.search);
      newParams.set("serviceId", serviceId);
      navigate(location.pathname + "?" + newParams.toString());
    },
    [location, navigate],
  );

  const handlePackageClick = useCallback(
    (serviceId, packageId) => {
      const preservedParams = preserveParams(location.search);
      preservedParams.set("pteamId", pteamId);
      preservedParams.set("serviceId", serviceId);
      navigate(`/packages/${packageId}?${preservedParams.toString()}`);
    },
    [location.search, navigate, pteamId],
  );

  return (
    <>
      <Box display="flex" flexDirection="row">
        <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
        <SBOMUploadProgressButton pteamId={pteamId} />
      </Box>
      <SBOMManagement
        initialSboms={sboms}
        initialActiveId={serviceId}
        onThumbnailChange={handleThumbnailChanged}
        onActiveIdChange={handleActiveIdChange}
        onPackageClick={handlePackageClick}
        pteamId={pteamId}
      />
    </>
  );
}

StatusBody.propTypes = {
  pteamId: PropTypes.string.isRequired,
  pteam: PropTypes.object.isRequired,
  serviceId: PropTypes.string,
};
