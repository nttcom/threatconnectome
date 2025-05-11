import { Button, Dialog, DialogActions, DialogContent, DialogContentText } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { DialogHeader } from "../DialogHeader";
import { CHANGE_EMAIL_DIALOG_STATES } from "../dialogStates";

export function SendVerificationEmailDialog(props) {
  const { open, setOpen, handleClose, userEmail } = props;

  const handleSendVerificationCode = () => {
    // TODO: Add logic to send a verification code to the user's email address
    console.log("Verification code sent to:", userEmail);
    setOpen(CHANGE_EMAIL_DIALOG_STATES.ENTER_VERIFICATION_CODE);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
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
  );
}

SendVerificationEmailDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  userEmail: PropTypes.string.isRequired,
  setOpen: PropTypes.func.isRequired,
};
