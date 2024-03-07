import { Close as CloseIcon } from "@mui/icons-material";
import { Box, Dialog, DialogContent, DialogTitle, IconButton, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

import { PTeamTagAutoClose } from "./PTeamTagAutoClose";

export function PTeamTagSettingsModal(props) {
  const { onSetShow, show, tagId } = props;

  const handleClose = () => onSetShow(false);

  return (
    <Dialog fullWidth onClose={handleClose} open={show}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
            Auto Close
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <PTeamTagAutoClose tagId={tagId} />
      </DialogContent>
    </Dialog>
  );
}
PTeamTagSettingsModal.propTypes = {
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  tagId: PropTypes.string.isRequired,
};
