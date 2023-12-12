import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { ATeamSettingsModal } from "./ATeamSettingsModal";
import { UUIDTypography } from "./UUIDTypography";

export function ATeamLabel(props) {
  const { ateam } = props;

  const [ateamSettingsModalOpen, setATeamSettingsModalOpen] = useState(false);

  return (
    <>
      <Box display="flex" flexDirection="column" flexGrow={1} my={2}>
        <Box display="flex" alignItems="center">
          <Typography variant="h5" fontWeight={900}>
            {ateam.ateam_name}
          </Typography>
          <IconButton onClick={() => setATeamSettingsModalOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
        <UUIDTypography>{ateam.ateam_id}</UUIDTypography>
      </Box>
      <ATeamSettingsModal
        setShow={setATeamSettingsModalOpen}
        show={ateamSettingsModalOpen}
        ateam={ateam}
      />
    </>
  );
}

ATeamLabel.propTypes = {
  ateam: PropTypes.object.isRequired,
};
