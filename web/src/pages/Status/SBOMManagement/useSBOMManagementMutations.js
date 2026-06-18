import { useSnackbar } from "notistack";
import { useTranslation } from "react-i18next";

import {
  useDeletePTeamServiceMutation,
  useDeletePTeamServiceThumbnailMutation,
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
} from "../../../services/tcApi";
import {
  createId,
  getNextActiveIdAfterRemoval,
  NEW_SBOM_ID,
} from "../../../utils/SBOMManagement/sbomManagementUtils";
import { serviceImageMaxSize } from "../../../utils/const";
import { errorToString } from "../../../utils/func";
import { normalizeServiceImageToPng } from "../../../utils/serviceImageUtils";

export function useSBOMManagementMutations({ actions, callbacks, state }) {
  const { activeId, activeService, isCreatingSbom, pendingThumbnail, pteamId, serviceTabs } = state;
  const {
    markClean,
    resetUiState,
    setActiveId,
    setDeploymentsEditing,
    setDetailsEditing,
    setPendingThumbnail,
    setPendingUpload,
    updateActiveService,
  } = actions;
  const { onActiveIdChange } = callbacks;
  const { t } = useTranslation("status", { keyPrefix: "useSBOMManagementMutations" });
  const { enqueueSnackbar } = useSnackbar();
  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const [deletePTeamService] = useDeletePTeamServiceMutation();
  const [updatePTeamServiceThumbnail] = useUpdatePTeamServiceThumbnailMutation();
  const [deletePTeamServiceThumbnail] = useDeletePTeamServiceThumbnailMutation();

  const removeActiveSbom = async () => {
    if (isCreatingSbom || !pteamId || !activeService) {
      return;
    }

    try {
      await deletePTeamService({
        path: { pteam_id: pteamId, service_id: activeService.id },
      }).unwrap();
      enqueueSnackbar(t("deleteSuccess"), { variant: "success" });
    } catch (error) {
      enqueueSnackbar(t("deleteFailed", { error: errorToString(error) }), { variant: "error" });
      return;
    }

    const nextActiveId = getNextActiveIdAfterRemoval(serviceTabs, activeId) || NEW_SBOM_ID;
    setActiveId(nextActiveId);
    onActiveIdChange?.(nextActiveId);
    resetUiState();
  };

  const addDeployment = () => {
    if (!activeService) {
      return;
    }

    updateActiveService({
      deployments: [...activeService.deployments, { id: createId("dep"), ip: "", location: "" }],
    });
  };

  const updateDeployment = (deploymentId, patch) => {
    if (!activeService) {
      return;
    }

    updateActiveService({
      deployments: activeService.deployments.map((deployment) =>
        deployment.id === deploymentId ? { ...deployment, ...patch } : deployment,
      ),
    });
  };

  const removeDeployment = (deploymentId) => {
    if (!activeService) {
      return;
    }

    const confirmed = typeof window === "undefined" || window.confirm(t("confirmRemoveDeployment"));

    if (!confirmed) {
      return;
    }

    updateActiveService({
      deployments: activeService.deployments.filter((deployment) => deployment.id !== deploymentId),
    });
  };

  const openUpdateSbomDialog = () => {
    if (!activeService) {
      return;
    }

    setPendingUpload({ serviceName: activeService.title });
  };

  const handleImageUpload = async (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file || !activeService) {
      return;
    }

    if (file.size >= serviceImageMaxSize) {
      enqueueSnackbar(t("imageTooLarge"), { variant: "error" });
      return;
    }

    try {
      const normalized = await normalizeServiceImageToPng(file);
      if (normalized.file.size >= serviceImageMaxSize) {
        enqueueSnackbar(t("imageTooLargeAfterConvert"), { variant: "error" });
        return;
      }
      setPendingThumbnail({
        file: normalized.file,
        previewDataUrl: normalized.previewDataUrl,
        deleted: false,
      });
    } catch {
      enqueueSnackbar(t("imageProcessFailed"), { variant: "error" });
    }
  };

  const handleRemoveImage = () => {
    setPendingThumbnail({ file: null, previewDataUrl: null, deleted: true });
  };

  const commitDetailsEdit = async () => {
    if (!activeService || !pteamId) {
      setDetailsEditing(false);
      return;
    }

    if (!activeService.title.trim()) {
      enqueueSnackbar(t("serviceNameRequired"), { variant: "error" });
      return;
    }

    const calls = [];

    calls.push(() =>
      updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeService.id },
        body: {
          service_name: activeService.title.trim(),
          description: activeService.description.trim(),
          keywords: activeService.tags,
        },
      }).unwrap(),
    );

    if (pendingThumbnail?.file) {
      const file = pendingThumbnail.file;
      calls.push(() =>
        updatePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: activeService.id },
          body: { uploaded: file },
        }).unwrap(),
      );
    } else if (pendingThumbnail?.deleted) {
      calls.push(() =>
        deletePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: activeService.id },
        }).unwrap(),
      );
    }

    try {
      await Promise.all(calls.map((fn) => fn()));
      enqueueSnackbar(t("updateDetailsSuccess"), { variant: "success" });
      setPendingThumbnail(null);
      setDetailsEditing(false);
      markClean();
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
    }
  };

  const commitDeploymentsEdit = async () => {
    if (!activeService || !pteamId) {
      setDeploymentsEditing(false);
      return;
    }

    const ipAddresses = activeService.deployments
      .map((deployment) => deployment.ip.trim())
      .filter(Boolean);

    try {
      await updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeService.id },
        body: { asset: { ip_addresses: ipAddresses } },
      }).unwrap();
      enqueueSnackbar(t("updateDeploymentsSuccess"), { variant: "success" });
      setDeploymentsEditing(false);
      markClean();
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
    }
  };

  const commitServiceImpactEdit = async ({ missionImpact, systemExposure }) => {
    if (!activeService || !pteamId) {
      return true;
    }

    if (
      systemExposure === activeService.systemExposure &&
      missionImpact === activeService.missionImpact
    ) {
      return true;
    }

    try {
      await updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeService.id },
        body: {
          system_exposure: systemExposure,
          service_mission_impact: missionImpact,
        },
      }).unwrap();
      enqueueSnackbar(t("updateRiskSettingsSuccess"), { variant: "success" });
      markClean();
      return true;
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
      return false;
    }
  };

  return {
    addDeployment,
    commitDeploymentsEdit,
    commitDetailsEdit,
    commitServiceImpactEdit,
    openUpdateSbomDialog,
    handleImageUpload,
    handleRemoveImage,
    removeActiveSbom,
    removeDeployment,
    updateDeployment,
  };
}
