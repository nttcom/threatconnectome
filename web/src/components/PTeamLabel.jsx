import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../hooks/auth";
import { useGetUserMeQuery } from "../services/tcApi";
import { APIError } from "../utils/APIError";
import { errorToString } from "../utils/func";

import { PTeamSettingsModal } from "./PTeamSettingsModal";
import { UUIDTypography } from "./UUIDTypography";

export function PTeamLabel(props) {
  const { pteamId, defaultTabIndex = 0 } = props;

  const [pteamSettingsModalOpen, setPTeamSettingsModalOpen] = useState(false);

  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const pteamName =
    userMe.pteam_roles.find((pteam_role) => pteam_role.pteam.pteam_id === pteamId)?.pteam
      .pteam_name ?? "-";

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
  pteamId: PropTypes.string.isRequired,
  defaultTabIndex: PropTypes.number,
};
