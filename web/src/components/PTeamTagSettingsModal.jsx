import { Close as CloseIcon } from "@mui/icons-material";
import { Box, Dialog, DialogContent, DialogTitle, IconButton, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import dialogStyle from "../cssModule/dialog.module.css";

import { PTeamTagAutoClose } from "./PTeamTagAutoClose";

export function PTeamTagSettingsModal(props) {
  const { onSetShow, show, tagId } = props;

  const handleClose = () => onSetShow(false);

  return (
    <Dialog open={show} onClose={handleClose} fullWidth>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            Auto Close
          </Typography>
          <IconButton onClick={handleClose}>
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
