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
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit">
            {text} is in progress. Please wait.
          </Typography>
          <CircularProgress />
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
