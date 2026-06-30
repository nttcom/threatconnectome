import { useSnackbar } from "notistack";
import type { ChangeEvent } from "react";
import { useTranslation } from "react-i18next";

import {
  useDeletePTeamServiceMutation,
  useDeletePTeamServiceThumbnailMutation,
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
} from "../../../services/tcApi";
import {
  getNextActiveIdAfterRemoval,
  NEW_SBOM_ID,
  normalizeCommaSeparatedValues,
} from "../../../utils/SBOMManagement/sbomManagementUtils";
import { serviceImageMaxSize } from "../../../utils/const";
import { errorToString } from "../../../utils/func";
import { normalizeServiceImageToPng } from "../../../utils/serviceImageUtils";

import type {
  OnActiveIdChange,
  PendingThumbnail,
  SbomService,
  SbomServicePatch,
  SbomServiceTab,
} from "./SBOMManagementTypes";

type MutationActions = {
  markClean: () => void;
  resetUiState: () => void;
  setActiveId: (serviceId: string) => void;
  setDeploymentsEditing: (value: boolean) => void;
  setDetailsEditing: (value: boolean) => void;
  setPendingThumbnail: (value: PendingThumbnail | null) => void;
  setPendingUpload: (value: { initialFile?: File; serviceName?: string } | null) => void;
  updateActiveService: (patch: SbomServicePatch) => void;
};

type MutationState = {
  activeId: string;
  activeService: SbomService | null;
  isCreatingSbom: boolean;
  pendingThumbnail: PendingThumbnail | null;
  pteamId: string;
  serviceTabs: SbomServiceTab[];
};

export function useSBOMManagementMutations({
  actions,
  callbacks,
  state,
}: {
  actions: MutationActions;
  callbacks: { onActiveIdChange?: OnActiveIdChange };
  state: MutationState;
}) {
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
      enqueueSnackbar(
        t("deleteFailed", { error: errorToString(error as Parameters<typeof errorToString>[0]) }),
        {
          variant: "error",
        },
      );
      return;
    }

    const nextActiveId = getNextActiveIdAfterRemoval(serviceTabs, activeId) || NEW_SBOM_ID;
    setActiveId(nextActiveId);
    onActiveIdChange?.(nextActiveId);
    resetUiState();
  };

  const updateDeploymentSettings = (patch: SbomServicePatch) => {
    if (!activeService) {
      return;
    }

    updateActiveService(patch);
  };

  const openUpdateSbomDialog = () => {
    if (!activeService) {
      return;
    }

    setPendingUpload({ serviceName: activeService.title });
  };

  const handleImageUpload = async (event: ChangeEvent<HTMLInputElement>) => {
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
      enqueueSnackbar(
        t("updateFailed", { error: errorToString(error as Parameters<typeof errorToString>[0]) }),
        {
          variant: "error",
        },
      );
    }
  };

  const commitDeploymentsEdit = async () => {
    if (!activeService || !pteamId) {
      setDeploymentsEditing(false);
      return;
    }

    const ipAddresses = normalizeCommaSeparatedValues((activeService.ipAddresses || []).join(","));
    const countryCode = (activeService.countryCode || "").trim().toUpperCase();
    const address = (activeService.address || "").trim();

    try {
      await updatePTeamService({
        path: { pteam_id: pteamId, service_id: activeService.id },
        body: {
          asset: {
            ip_addresses: ipAddresses,
            country_code: countryCode || null,
            address: address || null,
          },
        },
      }).unwrap();
      enqueueSnackbar(t("updateDeploymentsSuccess"), { variant: "success" });
      setDeploymentsEditing(false);
      markClean();
    } catch (error) {
      enqueueSnackbar(
        t("updateFailed", { error: errorToString(error as Parameters<typeof errorToString>[0]) }),
        {
          variant: "error",
        },
      );
    }
  };

  const commitServiceImpactEdit = async ({
    missionImpact,
    systemExposure,
  }: Pick<SbomService, "missionImpact" | "systemExposure">) => {
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
      enqueueSnackbar(
        t("updateFailed", { error: errorToString(error as Parameters<typeof errorToString>[0]) }),
        {
          variant: "error",
        },
      );
      return false;
    }
  };

  return {
    commitDeploymentsEdit,
    commitDetailsEdit,
    commitServiceImpactEdit,
    openUpdateSbomDialog,
    handleImageUpload,
    handleRemoveImage,
    removeActiveSbom,
    updateDeploymentSettings,
  };
}
