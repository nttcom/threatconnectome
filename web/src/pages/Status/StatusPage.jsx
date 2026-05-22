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
import { preserveMyTasksParam } from "../../utils/urlUtils";

import { SBOMManagement } from "./SBOMManagement";
import { FileDropZone } from "./SbomDrop/FileDropZone";
import { SBOMUpdateDialog } from "./SbomDrop/SBOMUpdateDialog";
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

  const [selectedFile, setSelectedFile] = useState(null);
  const [sbomUpdateDialogOpen, setSbomUpdateDialogOpen] = useState(false);

  const handleFileSelected = (file) => {
    setSelectedFile(file);
    setSbomUpdateDialogOpen(true);
  };

  const handleSbomUpdateDialogClose = () => {
    setSelectedFile(null);
    setSbomUpdateDialogOpen(false);
  };

  const {
    data: pteam,
    error: pteamError,
    isFetching: pteamIsFetching,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip: skipByAuth || !pteamId });

  const {
    currentData: packagesSummary,
    error: packagesSummaryError,
    isFetching: packagesSummaryIsFetching,
  } = useGetPTeamPackagesSummaryQuery(
    { path: { pteam_id: pteamId } },
    { skip: skipByAuth || !pteamId },
  );

  useEffect(() => {
    if (!pteamId) return;
    if (pteamIsFetching || !pteam) return;
    if (!serviceId && pteam.services.length > 0) {
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      newParams.set("serviceId", pteam.services[0].service_id);
      const mytasksParam = preserveMyTasksParam(location.search);
      for (const [key, value] of mytasksParam) {
        newParams.set(key, value);
      }
      navigate(location.pathname + "?" + newParams.toString());
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, pteam, pteamIsFetching, serviceId]);

  if (!pteamId) return <>{getNoPTeamMessage()}</>;
  if (skipByAuth) return <></>;
  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamIsLoading) return <>{t("loading_team")}</>;
  if (packagesSummaryError)
    throw new APIError(errorToString(packagesSummaryError), { api: "getPTeamPackagesSummary" });

  if (pteam.services.length === 0) {
    return (
      <>
        <Box display="flex" flexDirection="row">
          <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
          <Box flexGrow={1} />
        </Box>
        <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
          <SBOMUploadProgressButton pteamId={pteamId} />
        </Box>
        <FileDropZone
          onFileSelected={handleFileSelected}
          selectedFile={null}
          showFileName={false}
        />
        <SBOMUpdateDialog
          open={sbomUpdateDialogOpen}
          onClose={handleSbomUpdateDialogClose}
          pteamId={pteamId}
          initialFile={selectedFile}
          onUploaded={() => {}}
          showWarning={false}
        />
      </>
    );
  }

  if (packagesSummaryIsFetching || !packagesSummary) {
    return <>{t("loading_packages_summary")}</>;
  }

  return (
    <StatusBody
      pteamId={pteamId}
      pteam={pteam}
      packagesSummary={packagesSummary}
      initialActiveServiceId={serviceId}
    />
  );
}

function StatusBody({ pteamId, pteam, packagesSummary, initialActiveServiceId }) {
  const [thumbnails, setThumbnails] = useState({});

  const handleThumbnailLoaded = useCallback((serviceId, dataUrl) => {
    setThumbnails((prev) =>
      prev[serviceId] === dataUrl ? prev : { ...prev, [serviceId]: dataUrl },
    );
  }, []);

  const sboms = useMemo(() => {
    const base = buildSbomsFromPTeam(pteam.services, packagesSummary.packages);
    return base.map((sbom) => ({ ...sbom, imageUrl: thumbnails[sbom.id] || "" }));
  }, [pteam.services, packagesSummary.packages, thumbnails]);

  return (
    <>
      <Box display="flex" flexDirection="row">
        <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
        <SBOMUploadProgressButton pteamId={pteamId} />
      </Box>
      {pteam.services.map((service) => (
        <ServiceThumbnailLoader
          key={service.service_id}
          pteamId={pteamId}
          serviceId={service.service_id}
          onLoaded={handleThumbnailLoaded}
        />
      ))}
      <SBOMManagement initialSboms={sboms} initialActiveId={initialActiveServiceId} />
    </>
  );
}

StatusBody.propTypes = {
  pteamId: PropTypes.string.isRequired,
  pteam: PropTypes.object.isRequired,
  packagesSummary: PropTypes.object.isRequired,
  initialActiveServiceId: PropTypes.string,
};
