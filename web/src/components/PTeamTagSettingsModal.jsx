import { Close as CloseIcon } from "@mui/icons-material";
import { Box, Dialog, DialogContent, DialogTitle, IconButton, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

import { PTeamAutoClose } from "./PTeamAutoClose";

export function PTeamTagSettingsModal(props) {
  const { setShow, show } = props;

  const handleClose = () => setShow(false);

  return (
    <Dialog fullWidth onClose={handleClose} open={show}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
            Tag Close
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <PTeamAutoClose />
      </DialogContent>
    </Dialog>
  );
}
PTeamTagSettingsModal.propTypes = {
  setShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
};
