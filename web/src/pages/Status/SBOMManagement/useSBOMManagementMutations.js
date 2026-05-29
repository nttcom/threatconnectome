import { useSnackbar } from "notistack";
import { useTranslation } from "react-i18next";

import {
  useDeletePTeamServiceMutation,
  useDeletePTeamServiceThumbnailMutation,
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
} from "../../../services/tcApi";
import { serviceImageMaxSize } from "../../../utils/const";
import { errorToString } from "../../../utils/func";
import {
  createId,
  getNextActiveIdAfterRemoval,
  NEW_SBOM_ID,
} from "../../../utils/SBOMManagement/sbomManagementUtils";
import { normalizeServiceImageToPng } from "../../../utils/serviceImageUtils";

export function useSBOMManagementMutations({
  activeId,
  activeSbom,
  isCreatingSbom,
  onActiveIdChange,
  onThumbnailChange,
  pteamId,
  resetUiState,
  sboms,
  setActiveId,
  setDeploymentsEditing,
  setDetailsEditing,
  setPendingThumbnail,
  setPendingUpload,
  updateActiveSbom,
  updateActiveSbomImage,
}) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMManagement" });
  const { enqueueSnackbar } = useSnackbar();
  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const [deletePTeamService] = useDeletePTeamServiceMutation();
  const [updatePTeamServiceThumbnail] = useUpdatePTeamServiceThumbnailMutation();
  const [deletePTeamServiceThumbnail] = useDeletePTeamServiceThumbnailMutation();

  const removeActiveSbom = async () => {
    if (isCreatingSbom || !pteamId || !activeSbom) {
      return;
    }

    try {
      await deletePTeamService({
        path: { pteam_id: pteamId, service_id: activeSbom.id },
      }).unwrap();
      enqueueSnackbar(t("deleteSuccess"), { variant: "success" });
    } catch (error) {
      enqueueSnackbar(t("deleteFailed", { error: errorToString(error) }), { variant: "error" });
      return;
    }

    const nextActiveId = getNextActiveIdAfterRemoval(sboms, activeId) || NEW_SBOM_ID;
    setActiveId(nextActiveId);
    onActiveIdChange?.(nextActiveId);
    resetUiState();
  };

  const addDeployment = () => {
    if (!activeSbom) {
      return;
    }

    updateActiveSbom({
      deployments: [...activeSbom.deployments, { id: createId("dep"), ip: "", location: "" }],
    });
  };

  const updateDeployment = (deploymentId, patch) => {
    if (!activeSbom) {
      return;
    }

    updateActiveSbom({
      deployments: activeSbom.deployments.map((deployment) =>
        deployment.id === deploymentId ? { ...deployment, ...patch } : deployment,
      ),
    });
  };

  const removeDeployment = (deploymentId) => {
    if (!activeSbom) {
      return;
    }

    const confirmed = typeof window === "undefined" || window.confirm(t("confirmRemoveDeployment"));

    if (!confirmed) {
      return;
    }

    updateActiveSbom({
      deployments: activeSbom.deployments.filter((deployment) => deployment.id !== deploymentId),
    });
  };

  const handleFileUpload = (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file || !activeSbom) {
      return;
    }

    setPendingUpload({ file, serviceName: activeSbom.title });
  };

  const handleImageUpload = async (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file || !activeSbom) {
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

  const commitDetailsEdit = async (pendingThumbnail) => {
    if (!activeSbom || !pteamId) {
      setDetailsEditing(false);
      return;
    }

    const calls = [];

    calls.push(() =>
      updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeSbom.id },
        body: {
          service_name: activeSbom.title.trim(),
          description: activeSbom.description.trim(),
          keywords: activeSbom.tags,
        },
      }).unwrap(),
    );

    if (pendingThumbnail?.file) {
      const file = pendingThumbnail.file;
      calls.push(() =>
        updatePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: activeSbom.id },
          body: { uploaded: file },
        }).unwrap(),
      );
    } else if (pendingThumbnail?.deleted) {
      calls.push(() =>
        deletePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: activeSbom.id },
        }).unwrap(),
      );
    }

    try {
      await Promise.all(calls.map((fn) => fn()));
      if (pendingThumbnail?.file) {
        const nextImageUrl = pendingThumbnail.previewDataUrl || "";
        onThumbnailChange?.(activeSbom.id, nextImageUrl);
        updateActiveSbomImage(nextImageUrl);
      } else if (pendingThumbnail?.deleted) {
        onThumbnailChange?.(activeSbom.id, "");
        updateActiveSbomImage("");
      }
      updateActiveSbom({
        title: activeSbom.title.trim(),
        description: activeSbom.description.trim(),
      });
      enqueueSnackbar(t("updateDetailsSuccess"), { variant: "success" });
      setPendingThumbnail(null);
      setDetailsEditing(false);
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
    }
  };

  const commitDeploymentsEdit = async () => {
    if (!activeSbom || !pteamId) {
      setDeploymentsEditing(false);
      return;
    }

    const ipAddresses = activeSbom.deployments
      .map((deployment) => deployment.ip.trim())
      .filter(Boolean);

    try {
      const updatedService = await updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeSbom.id },
        body: { asset: { ip_addresses: ipAddresses } },
      }).unwrap();
      updateActiveSbom({
        deployments: (updatedService.asset?.ip_addresses ?? []).map((ipAddress, index) => ({
          id: `dep-${activeSbom.id}-${index}`,
          ip: ipAddress,
          location: "",
        })),
      });
      enqueueSnackbar(t("updateDeploymentsSuccess"), { variant: "success" });
      setDeploymentsEditing(false);
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
    }
  };

  const commitServiceImpactEdit = async ({ missionImpact, systemExposure }) => {
    if (!activeSbom || !pteamId) {
      return true;
    }

    if (
      systemExposure === activeSbom.systemExposure &&
      missionImpact === activeSbom.missionImpact
    ) {
      return true;
    }

    try {
      const updatedService = await updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeSbom.id },
        body: {
          system_exposure: systemExposure,
          service_mission_impact: missionImpact,
        },
      }).unwrap();
      updateActiveSbom({
        systemExposure: updatedService?.system_exposure ?? systemExposure,
        missionImpact: updatedService?.service_mission_impact ?? missionImpact,
      });
      enqueueSnackbar(t("updateRiskSettingsSuccess"), { variant: "success" });
      return true;
    } catch (error) {
      enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
      return false;
    }
  };

  const handleCreateFileUpload = (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file) {
      return;
    }

    setPendingUpload({ file });
  };

  return {
    addDeployment,
    commitDeploymentsEdit,
    commitDetailsEdit,
    commitServiceImpactEdit,
    handleCreateFileUpload,
    handleFileUpload,
    handleImageUpload,
    handleRemoveImage,
    removeActiveSbom,
    removeDeployment,
    updateDeployment,
  };
}
