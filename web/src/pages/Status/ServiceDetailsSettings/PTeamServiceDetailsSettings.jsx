import { useSnackbar } from "notistack";
import PropTypes from "prop-types";

import {
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamServiceThumbnailQuery,
} from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { PTeamServiceDetailsSettingsView } from "./PTeamServiceDetailsSettingsView";

const serviceDetailsSetttingNoImageUrl = "images/720x480.png";

export function PTeamServiceDetailsSettings(props) {
  const { pteamId, service } = props;

  const { enqueueSnackbar } = useSnackbar();

  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const [updatePTeamServiceThumbnail] = useUpdatePTeamServiceThumbnailMutation();
  const [deletePTeamServiceThumbnail] = useDeletePTeamServiceThumbnailMutation();

  const handleSave = async (
    serviceName,
    imageFileData,
    imageDeleteFalg,
    keywordsList,
    description,
    defaultSafetyImpactValue,
  ) => {
    const promiseList = [];

    if (imageFileData !== null) {
      promiseList.push(() =>
        updatePTeamServiceThumbnail({
          pteamId: pteamId,
          serviceId: service.service_id,
          imageFile: imageFileData,
        }).unwrap(),
      );
    }

    if (imageDeleteFalg) {
      promiseList.push(() =>
        deletePTeamServiceThumbnail({
          pteamId: pteamId,
          serviceId: service.service_id,
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
        pteamId: pteamId,
        serviceId: service.service_id,
        data: requestData,
      }).unwrap(),
    );

    Promise.all(promiseList.map((apiFunc) => apiFunc()))
      .then(() => {
        enqueueSnackbar("Update succeeded", { variant: "success" });
      })
      .catch((error) => {
        enqueueSnackbar(`Update failed: ${errorToString(error)}`, { variant: "error" });
      });
  };

  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    pteamId,
    serviceId: service.service_id,
  });

  const image =
    thumbnailIsError || thumbnailIsLoading || !thumbnail
      ? serviceDetailsSetttingNoImageUrl
      : thumbnail;

  return <PTeamServiceDetailsSettingsView service={service} image={image} onSave={handleSave} />;
}

PTeamServiceDetailsSettings.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
};
