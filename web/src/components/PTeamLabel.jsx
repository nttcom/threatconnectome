import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetUserMeQuery } from "../services/tcApi";
import { errorToString } from "../utils/func";

import { PTeamSettingsModal } from "./PTeamSettingsModal";
import { UUIDTypography } from "./UUIDTypography";

export function PTeamLabel(props) {
  const { defaultTabIndex = 0 } = props;

  const [pteamSettingsModalOpen, setPTeamSettingsModalOpen] = useState(false);

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  const pteamId = useSelector((state) => state.pteam.pteamId); // dispatched by App or PTeamSelector

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const pteamName = userMe.pteams.find((pteam) => pteam.pteam_id === pteamId)?.pteam_name ?? "-";

  return (
    <>
      <Box display="flex" flexDirection="column" flexGrow={1} my={2}>
        <Box display="flex" alignItems="center">
          <Typography variant="h5" fontWeight={900}>
            {pteamName}
          </Typography>
          <IconButton onClick={() => setPTeamSettingsModalOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
        <UUIDTypography>{pteamId}</UUIDTypography>
      </Box>
      <PTeamSettingsModal
        pteamId={pteamId}
        onSetShow={setPTeamSettingsModalOpen}
        show={pteamSettingsModalOpen}
        defaultTabIndex={defaultTabIndex}
      />
    </>
  );
}

PTeamLabel.propTypes = {
  defaultTabIndex: PropTypes.number,
};
