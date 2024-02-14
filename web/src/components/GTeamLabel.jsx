import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { GTeamSettingsModal } from "./GTeamSettingsModal";
import { UUIDTypography } from "./UUIDTypography";

export function GTeamLabel(props) {
  const { gteam } = props;

  const [gteamSettingsModalOpen, setGTeamSettingsModalOpen] = useState(false);

  return (
    <>
      <Box display="flex" flexDirection="column" flexGrow={1} my={2}>
        <Box display="flex" alignItems="center">
          <Typography variant="h5" fontWeight={900}>
            {gteam.gteam_name}
          </Typography>
          <IconButton onClick={() => setGTeamSettingsModalOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
        <UUIDTypography>{gteam.gteam_id}</UUIDTypography>
      </Box>
      <GTeamSettingsModal
        onSetShow={setGTeamSettingsModalOpen}
        show={gteamSettingsModalOpen}
        gteam={gteam}
      />
    </>
  );
}

GTeamLabel.propTypes = {
  gteam: PropTypes.object.isRequired,
};
