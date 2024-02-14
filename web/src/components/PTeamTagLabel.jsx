import { Settings as SettingsIcon } from "@mui/icons-material";
import { Box, IconButton } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { PTeamTagSettingsModal } from "./PTeamTagSettingsModal";

export function PTeamTagLabel(props) {
  const { tagId } = props;
  const [pteamTagSettingsModalOpen, setPTeamTagSettingsModalOpen] = useState(false);

  return (
    <>
      <Box display="flex" flexDirection="column">
        <Box display="flex" alignItems="center">
          <IconButton onClick={() => setPTeamTagSettingsModalOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>
      <PTeamTagSettingsModal
        onSetShow={setPTeamTagSettingsModalOpen}
        show={pteamTagSettingsModalOpen}
        tagId={tagId}
      />
    </>
  );
}

PTeamTagLabel.propTypes = {
  tagId: PropTypes.string.isRequired,
};
