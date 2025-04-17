import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  Stack,
  TextField,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { DialogHeader } from "./DialogHeader";
import { UPDATE_PASSWORD_DIALOG_STATES } from "./dialogStates";

export function UpdatePasswordDialog(props) {
  const { open, setOpen } = props;

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [currentPasswordError, setCurrentPasswordError] = useState("");
  const [newPasswordError, setNewPasswordError] = useState("");
  const [confirmPasswordError, setConfirmPasswordError] = useState("");

  const validateCurrentPassword = () => {
    if (!currentPassword) {
      setCurrentPasswordError("Current password is required.");
      return false;
    }
    setCurrentPasswordError("");
    return true;
  };

  const validateNewPassword = () => {
    if (!newPassword) {
      setNewPasswordError("New password is required.");
      return false;
    }
    setNewPasswordError("");
    return true;
  };

  const validateConfirmPassword = () => {
    if (!confirmPassword) {
      setConfirmPasswordError("Please confirm your new password.");
      return false;
    }
    if (newPassword !== confirmPassword) {
      setConfirmPasswordError("New password and confirmation do not match.");
      return false;
    }
    setConfirmPasswordError("");
    return true;
  };

  const handleClose = () => {
    setOpen(UPDATE_PASSWORD_DIALOG_STATES.NONE);
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setCurrentPasswordError("");
    setNewPasswordError("");
    setConfirmPasswordError("");
  };

  const handleUpdatePassword = () => {
    // validation for each field
    const isCurrentPasswordValid = validateCurrentPassword();
    const isNewPasswordValid = validateNewPassword();
    const isConfirmPasswordValid = validateConfirmPassword();

    // All validations must succeed to proceed
    if (!isCurrentPasswordValid || !isNewPasswordValid || !isConfirmPasswordValid) {
      return;
    }

    // TODO: Add logic for updating the password
    console.log("Password updated successfully!");
    handleClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogHeader title="Update your password" onClose={handleClose} />
      <DialogContent>
        <DialogContentText>
          Enter your current password and new password. Your new password must be at least 8
          characters long.
        </DialogContentText>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <TextField
            hiddenLabel
            size="small"
            label="Current password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            error={!!currentPasswordError}
            helperText={currentPasswordError}
          />
          <TextField
            hiddenLabel
            size="small"
            label="New password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            error={!!newPasswordError}
            helperText={newPasswordError}
          />
          <TextField
            hiddenLabel
            size="small"
            label="Confirm your new password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            error={!!confirmPasswordError}
            helperText={confirmPasswordError}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleUpdatePassword}>
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
