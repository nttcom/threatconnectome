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

import { DialogHeader } from "../DialogHeader";
import { CHANGE_EMAIL_DIALOG_STATES } from "../dialogStates";

export function EnterVerificationCodeDialog(props) {
  const {
    open,
    setOpen,
    handleClose,
    userEmail,
    verificationCode,
    setVerificationCode,
    errors,
    setErrors,
  } = props;

  const validateVerificationCode = () => {
    const newErrors = {};
    if (!verificationCode) {
      newErrors.verificationCode = "Verification code is required.";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleVerifyCode = () => {
    if (validateVerificationCode()) {
      // TODO: Add logic to verify the entered verification code
      console.log("Verification code verified successfully!");
      setOpen(CHANGE_EMAIL_DIALOG_STATES.CHANGE_EMAIL_FORM);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
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
  );
}

EnterVerificationCodeDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  userEmail: PropTypes.string.isRequired,
  setOpen: PropTypes.func.isRequired,
  verificationCode: PropTypes.string.isRequired,
  setVerificationCode: PropTypes.func.isRequired,
  errors: PropTypes.object.isRequired,
  setErrors: PropTypes.func.isRequired,
};
