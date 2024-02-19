import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  CircularProgress,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export function WaitingModal(props) {
  const { isOpen, text } = props;

  return (
    <Dialog fullWidth open={isOpen}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row" sx={{ mt: 3 }}>
          <Typography flexGrow={1} variant="inherit" sx={{ ml: 2 }}>
            {text} is in progress. Please wait.
          </Typography>
          <CircularProgress sx={{ mr: 4 }} />
        </Box>
      </DialogTitle>
      <DialogContent></DialogContent>
    </Dialog>
  );
}
WaitingModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  text: PropTypes.string.isRequired,
};
