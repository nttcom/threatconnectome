import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  TextField,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { DialogHeader } from "./DialogHeader";
import { UPDATE_PASSWORD_DIALOG_STATES } from "./dialogStates";

export function UpdatePasswordDialog(props) {
  const { open, setOpen } = props;
  const handleClose = () => {
    setOpen(UPDATE_PASSWORD_DIALOG_STATES.NONE);
  };
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogHeader title="Update your password" onClose={handleClose} />
      <DialogContent>
        <DialogContentText>
          Enter your current password and new password. Your new password must be at least 8
          characters long.
        </DialogContentText>
        <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="Current password" />
        <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="New password" />
        <TextField
          hiddenLabel
          size="small"
          sx={{ width: 1, mt: 2 }}
          label="Confirm your new password"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          /* Add password update logic here */
          onClick={handleClose}
        >
          Update your password
        </Button>
      </DialogActions>
    </Dialog>
  );
}

UpdatePasswordDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
};
