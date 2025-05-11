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
import React from "react";

import { DialogHeader } from "../DialogHeader";

export default function ChangeEmailFormDialog(props) {
  const {
    open,
    handleClose,
    newEmail,
    setNewEmail,
    currentPassword,
    setCurrentPassword,
    errors,
    setErrors,
  } = props;

  const validateEmailFormat = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateChangeEmail = () => {
    const newErrors = {};
    if (!newEmail) {
      newErrors.newEmail = "New email address is required.";
    } else if (!validateEmailFormat(newEmail)) {
      newErrors.newEmail = "Invalid email address.";
    }
    if (!currentPassword) {
      newErrors.currentPassword = "Current password is required.";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChangeEmail = () => {
    if (validateChangeEmail()) {
      // TODO: Add logic to update the user's email address in the system
      console.log("Email changed successfully!");
      handleClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogHeader title="Change your email address" onClose={handleClose} />
      <DialogContent>
        <DialogContentText>Enter a new email address and your existing password.</DialogContentText>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <TextField
            hiddenLabel
            size="small"
            label="New email address"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            error={!!errors.newEmail}
            helperText={errors.newEmail}
          />
          <TextField
            hiddenLabel
            size="small"
            label="Current password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            error={!!errors.currentPassword}
            helperText={errors.currentPassword}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleChangeEmail}>
          Change email
        </Button>
      </DialogActions>
    </Dialog>
  );
}

ChangeEmailFormDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  setOpen: PropTypes.func.isRequired,
  userEmail: PropTypes.string.isRequired,
  newEmail: PropTypes.string.isRequired,
  currentPassword: PropTypes.string.isRequired,
  errors: PropTypes.object.isRequired,
  setErrors: PropTypes.func.isRequired,
  setNewEmail: PropTypes.func.isRequired,
  setCurrentPassword: PropTypes.func.isRequired,
};
