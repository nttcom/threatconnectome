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
import { CHANGE_EMAIL_DIALOG_STATES } from "./dialogStates";

export function ChangeEmailDialog(props) {
  const { open, setOpen } = props;

  const [newEmail, setNewEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [errors, setErrors] = useState({});

  const userEmail = "sample@example.com"; // Replace with actual email from user data

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

  const validateVerificationCode = () => {
    const newErrors = {};
    if (!verificationCode) {
      newErrors.verificationCode = "Verification code is required.";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleClose = () => {
    // Close the dialog and reset the state
    setNewEmail("");
    setCurrentPassword("");
    setVerificationCode("");
    setErrors({});
    setOpen(CHANGE_EMAIL_DIALOG_STATES.NONE);
  };

  const handleSendVerificationCode = () => {
    // TODO: Add logic to send a verification code to the user's email address
    console.log("Verification code sent to:", userEmail);
    setOpen(CHANGE_EMAIL_DIALOG_STATES.ENTER_VERIFICATION_CODE);
  };

  const handleVerifyCode = () => {
    if (validateVerificationCode()) {
      // TODO: Add logic to verify the entered verification code
      console.log("Verification code verified successfully!");
      setOpen(CHANGE_EMAIL_DIALOG_STATES.CHANGE_EMAIL);
    }
  };

  const handleChangeEmail = () => {
    if (validateChangeEmail()) {
      // TODO: Add logic to update the user's email address in the system
      console.log("Email changed successfully!");
      handleClose();
    }
  };

  return (
    <>
      <Dialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.SEND_VERIFICATION_EMAIL}
        onClose={handleClose}
        maxWidth="xs"
        fullWidth
      >
        <DialogHeader title="Verify email address" onClose={handleClose} />
        <DialogContent>
          <DialogContentText>
            {"Your current email address is "}
            <strong>{userEmail}</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleSendVerificationCode}>
            Send Verification Code
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.ENTER_VERIFICATION_CODE}
        onClose={handleClose}
        maxWidth="xs"
        fullWidth
      >
        <DialogHeader title="Enter Verification Code" onClose={handleClose} />
        <DialogContent>
          <DialogContentText>
            {"Your current email address is "}
            <strong>{userEmail}</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
          <TextField
            hiddenLabel
            size="small"
            sx={{ width: 1, mt: 2 }}
            placeholder="Enter Verification code"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            error={!!errors.verificationCode}
            helperText={errors.verificationCode}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleVerifyCode}>
            Continue
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.CHANGE_EMAIL}
        onClose={handleClose}
        maxWidth="xs"
        fullWidth
      >
        <DialogHeader title="Change your email address" onClose={handleClose} />
        <DialogContent>
          <DialogContentText>
            Enter a new email address and your existing password.
          </DialogContentText>
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
    </>
  );
}

ChangeEmailDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
};
