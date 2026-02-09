import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import {
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamServiceThumbnailQuery,
} from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { PTeamServiceDetailsSettingsView } from "./PTeamServiceDetailsSettingsView";

const serviceDetailsSettingNoImageUrl = "images/720x480.png";

export function PTeamServiceDetailsSettings(props) {
  const { pteamId, service, expandService } = props;
  const { t } = useTranslation("status", { keyPrefix: "PTeamServiceDetailsSettings" });

  const { enqueueSnackbar } = useSnackbar();

  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const [updatePTeamServiceThumbnail] = useUpdatePTeamServiceThumbnailMutation();
  const [deletePTeamServiceThumbnail] = useDeletePTeamServiceThumbnailMutation();

  const handleSave = async (
    serviceName,
    imageFileData,
    imageDeleteFlag,
    keywordsList,
    description,
    defaultSafetyImpactValue,
  ) => {
    const promiseList = [];

    if (imageFileData !== null) {
      promiseList.push(() =>
        updatePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: service.service_id },
          body: { uploaded: imageFileData },
        }).unwrap(),
      );
    }

    if (imageDeleteFlag) {
      promiseList.push(() =>
        deletePTeamServiceThumbnail({
          path: { pteam_id: pteamId, service_id: service.service_id },
        }).unwrap(),
      );
    }

    const requestData = {
      service_name: serviceName,
      keywords: keywordsList,
      description: description,
      service_safety_impact: defaultSafetyImpactValue,
    };
    promiseList.push(() =>
      updatePTeamService({
        path: { pteam_id: pteamId, service_id: service.service_id },
        body: requestData,
      }).unwrap(),
    );

    Promise.all(promiseList.map((apiFunc) => apiFunc()))
      .then(() => {
        enqueueSnackbar(t("updateSucceeded"), { variant: "success" });
      })
      .catch((error) => {
        enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
      });
  };

  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    path: { pteam_id: pteamId, service_id: service.service_id },
  });

  const image =
    thumbnailIsError || thumbnailIsLoading || !thumbnail
      ? serviceDetailsSettingNoImageUrl
      : thumbnail;

  return (
    <PTeamServiceDetailsSettingsView
      service={service}
      image={image}
      onSave={handleSave}
      expandService={expandService}
    />
  );
}

PTeamServiceDetailsSettings.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  expandService: PropTypes.bool.isRequired,
};
