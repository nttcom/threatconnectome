import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import { PTeamSettingsModal } from "./PTeamSettingsModal";
import { UUIDTypography } from "./UUIDTypography";

export function PTeamLabel(props) {
  const { defaultTabIndex } = props;

  const [pteamSettingsModalOpen, setPTeamSettingsModalOpen] = useState(false);

  const user = useSelector((state) => state.user.user);
  const pteamId = useSelector((state) => state.pteam.pteamId); // dispatched by App or PTeamSelector
  const pteamName = user.pteams.find((pteam) => pteam.pteam_id === pteamId)?.pteam_name ?? "-";

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
        setShow={setPTeamSettingsModalOpen}
        show={pteamSettingsModalOpen}
        defaultTabIndex={defaultTabIndex}
      />
    </>
  );
}

PTeamLabel.propTypes = {
  defaultTabIndex: PropTypes.number,
};
PTeamLabel.defaultProps = {
  defaultTabIndex: 0,
};
