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
import { CHANGE_EMAIL_DIALOG_STATES } from "./dialogStates";

export function ChangeEmailDialog(props) {
  const { open, setOpen } = props;
  const handleClose = () => {
    setOpen(CHANGE_EMAIL_DIALOG_STATES.NONE);
  };
  return (
    <>
      <Dialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.SEND_VERIFICATION_EMAIL}
        maxWidth="xs"
        fullWidth
      >
        <DialogHeader title="Verify email address" onClose={handleClose} />
        <DialogContent>
          <DialogContentText>
            {"Your current email address is "}
            <strong>sample@example.com</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => setOpen(CHANGE_EMAIL_DIALOG_STATES.ENTER_VERIFICATION_CODE)}
          >
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
            <strong>sample@example.com</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
          <TextField
            hiddenLabel
            size="small"
            sx={{ width: 1, mt: 2 }}
            placeholder="Enter Verification code"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => setOpen(CHANGE_EMAIL_DIALOG_STATES.CHANGE_EMAIL)}
          >
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
          <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="New email address" />
          <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="Current password" />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            variant="contained"
            /* Add email change logic here */
            onClick={handleClose}
          >
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
