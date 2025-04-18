import PropTypes from "prop-types";
import React, { useState } from "react";

import { CHANGE_EMAIL_DIALOG_STATES } from "../dialogStates";

import ChangeEmailFormDialog from "./ChangeEmailFormDialog";
import { EnterVerificationCodeDialog } from "./EnterVerificationCodeDialog";
import { SendVerificationEmailDialog } from "./SendVerificationEmailDialog";

export function ChangeEmailDialog(props) {
  const { open, setOpen } = props;

  const [newEmail, setNewEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [errors, setErrors] = useState({});

  const userEmail = "sample@example.com"; // Replace with actual email from user data

  const handleClose = () => {
    // Close the dialog and reset the state
    setNewEmail("");
    setCurrentPassword("");
    setVerificationCode("");
    setErrors({});
    setOpen(CHANGE_EMAIL_DIALOG_STATES.NONE);
  };

  return (
    <>
      <SendVerificationEmailDialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.SEND_VERIFICATION_EMAIL}
        setOpen={setOpen}
        handleClose={handleClose}
        userEmail={userEmail}
      />
      <EnterVerificationCodeDialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.ENTER_VERIFICATION_CODE}
        setOpen={setOpen}
        handleClose={handleClose}
        userEmail={userEmail}
        verificationCode={verificationCode}
        setVerificationCode={setVerificationCode}
        errors={errors}
        setErrors={setErrors}
      />
      <ChangeEmailFormDialog
        open={open === CHANGE_EMAIL_DIALOG_STATES.CHANGE_EMAIL_FORM}
        handleClose={handleClose}
        newEmail={newEmail}
        setNewEmail={setNewEmail}
        currentPassword={currentPassword}
        setCurrentPassword={setCurrentPassword}
        errors={errors}
        setErrors={setErrors}
      />
    </>
  );
}

ChangeEmailDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
};
