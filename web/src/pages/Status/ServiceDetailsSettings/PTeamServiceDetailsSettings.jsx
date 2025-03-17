import PropTypes from "prop-types";
import React from "react";

import {
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamServiceThumbnailQuery,
} from "../../../services/tcApi";

import { PTeamServiceDetailsSettingsView } from "./PTeamServiceDetailsSettingsView";

const serviceDetailsSetttingNoImageUrl = "images/720x480.png";

export function PTeamServiceDetailsSettings(props) {
  const { pteamId, service } = props;

  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const [updatePTeamServiceThumbnail] = useUpdatePTeamServiceThumbnailMutation();
  const [deletePTeamServiceThumbnail] = useDeletePTeamServiceThumbnailMutation();

  const updatePTeamServiceFunc = async (requestData) => {
    await updatePTeamService({
      pteamId: pteamId,
      serviceId: service.service_id,
      data: requestData,
    }).unwrap();
  };

  const updatePTeamServiceThumbnailFunc = async (imageFileData) => {
    await updatePTeamServiceThumbnail({
      pteamId: pteamId,
      serviceId: service.service_id,
      imageFile: imageFileData,
    }).unwrap();
  };

  const deletePTeamServiceThumbnailFunc = async () => {
    await deletePTeamServiceThumbnail({
      pteamId: pteamId,
      serviceId: service.service_id,
    }).unwrap();
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

  return (
    <PTeamServiceDetailsSettingsView
      service={service}
      updatePTeamServiceFunc={updatePTeamServiceFunc}
      updatePTeamServiceThumbnailFunc={updatePTeamServiceThumbnailFunc}
      deletePTeamServiceThumbnailFunc={deletePTeamServiceThumbnailFunc}
      image={image}
    />
  );
}

PTeamServiceDetailsSettings.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
};
