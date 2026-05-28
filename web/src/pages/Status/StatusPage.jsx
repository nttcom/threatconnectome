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
import { buildSbomsFromPTeam } from "../../utils/sbomManagementUtils";
import { preserveMyTasksParam, preserveParams } from "../../utils/urlUtils";

import { SBOMManagement } from "./SBOMManagement";
import { SBOMUploadProgressButton } from "./SbomProgress/SBOMUploadProgressButton";

function ServiceThumbnailLoader({ pteamId, serviceId, onLoaded }) {
  const { data: thumbnail } = useGetPTeamServiceThumbnailQuery({
    path: { pteam_id: pteamId, service_id: serviceId },
  });

  useEffect(() => {
    if (typeof thumbnail === "string") {
      onLoaded(serviceId, thumbnail);
    }
  }, [thumbnail, serviceId, onLoaded]);

  return null;
}

ServiceThumbnailLoader.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  onLoaded: PropTypes.func.isRequired,
};

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

    const serviceIds = pteam.services.map((service) => service.service_id);
    const serviceIdInPTeam = serviceId && serviceIds.includes(serviceId);
    const fallbackServiceId = pteam.services[0]?.service_id;
    if (serviceIdInPTeam || (!fallbackServiceId && !serviceId)) {
      return;
    }

    const newParams = new URLSearchParams();
    newParams.set("pteamId", pteamId);
    if (fallbackServiceId) {
      newParams.set("serviceId", fallbackServiceId);
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

  const serviceIdInPTeam =
    serviceId && pteam.services.some((service) => service.service_id === serviceId);
  if (pteam.services.length > 0 && !serviceIdInPTeam) return <></>;

  return (
    <StatusBody pteamId={pteamId} pteam={pteam} serviceId={serviceIdInPTeam ? serviceId : null} />
  );
}

function StatusBody({ pteamId, pteam, serviceId }) {
  const location = useLocation();
  const navigate = useNavigate();
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const [thumbnails, setThumbnails] = useState({});

  const { currentData: packagesSummary, error: packagesSummaryError } =
    useGetPTeamPackagesSummaryQuery(
      { path: { pteam_id: pteamId }, query: { service_id: serviceId } },
      {
        skip: skipByAuth || !pteamId || !serviceId,
      },
    );

  if (packagesSummaryError)
    throw new APIError(errorToString(packagesSummaryError), { api: "getPTeamPackagesSummary" });

  const handleThumbnailLoaded = useCallback((serviceId, dataUrl) => {
    setThumbnails((prev) =>
      prev[serviceId] === dataUrl ? prev : { ...prev, [serviceId]: dataUrl },
    );
  }, []);

  const sboms = useMemo(() => {
    const base = buildSbomsFromPTeam(pteam.services, packagesSummary?.packages ?? [], serviceId);
    return base.map((sbom) => ({ ...sbom, imageUrl: thumbnails[sbom.id] || "" }));
  }, [pteam.services, packagesSummary, serviceId, thumbnails]);

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
      {serviceId && (
        <ServiceThumbnailLoader
          key={serviceId}
          pteamId={pteamId}
          serviceId={serviceId}
          onLoaded={handleThumbnailLoaded}
        />
      )}
      <SBOMManagement
        initialSboms={sboms}
        initialActiveId={serviceId}
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
