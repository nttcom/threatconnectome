import PropTypes from "prop-types";
import React from "react";

import {
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
  useDeletePTeamServiceThumbnailMutation,
} from "../services/tcApi";

import { PTeamServiceDetailsSettingsView } from "./PTeamServiceDetailsSettingsView";

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

  return (
    <PTeamServiceDetailsSettingsView
      service={service}
      updatePTeamServiceFunc={updatePTeamServiceFunc}
      updatePTeamServiceThumbnailFunc={updatePTeamServiceThumbnailFunc}
      deletePTeamServiceThumbnailFunc={deletePTeamServiceThumbnailFunc}
    />
  );
}

PTeamServiceDetailsSettings.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
};
