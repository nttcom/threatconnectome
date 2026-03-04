import { Box, Button, Typography, Container } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { PasswordField } from "../../components/PasswordField";
import { useAuth } from "../../hooks/auth";

export default function ResetPasswordForm(props) {
  const { t } = useTranslation("emailVerification", { keyPrefix: "ResetPasswordForm" });
  const { oobCode } = props;
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState("");
  const [signUpForm, setSignUpForm] = useState({
    edited: new Set(),
    password: "",
    confirmPassword: "",
    isVisible: false,
    isConfirmVisible: false,
  });

  const { verifyPasswordResetCode, confirmPasswordReset } = useAuth();

  const showMessage = (text, type = "error") => {
    setMessage({ text, type });
  };

  async function handleResetPassword() {
    if (signUpForm.password !== signUpForm.confirmPassword) {
      showMessage(t("passwordsDoNotMatch"));
      return;
    }
    setDisabled(true);
    await verifyPasswordResetCode({ actionCode: oobCode })
      .then(() => confirmPasswordReset({ actionCode: oobCode, newPassword: signUpForm.password }))
      .then(() => showMessage(t("success"), "info"))
      .catch((error) => {
        console.error(error);
        showMessage(error.message);
      });
  }

  const handleVisibility = (prop) => {
    setSignUpForm((prev) => ({ ...prev, [prop]: !prev[prop] }));
  };

  const handleFormChange = (prop) => (event) => {
    signUpForm.edited.add(prop);
    setSignUpForm({
      ...signUpForm,
      [prop]: event.target.value,
    });
  };

  if (import.meta.env.VITE_AUTH_SERVICE === "supabase") {
    return <>{t("notSupported")}</>;
  }
  if (!oobCode) {
    return <>{t("missingCode")}</>;
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box alignItems="center" display="flex" flexDirection="column">
        <Typography variant="h5" my={2}>
          {t("title")}
        </Typography>
        <PasswordField
          name="password"
          label={t("newPassword")}
          value={signUpForm.password}
          edited={signUpForm.edited}
          onChange={handleFormChange("password")}
          isVisible={signUpForm.isVisible}
          onToggle={() => handleVisibility("isVisible")}
          tooltipTitle={t("passwordHint")}
        />
        <PasswordField
          name="confirmPassword"
          label={t("confirmPassword")}
          value={signUpForm.confirmPassword}
          edited={signUpForm.edited}
          onChange={handleFormChange("confirmPassword")}
          isVisible={signUpForm.isConfirmVisible}
          onToggle={() => handleVisibility("isConfirmVisible")}
          tooltipTitle={t("passwordHint")}
        />
        <Button
          onClick={() => handleResetPassword()}
          disabled={disabled || signUpForm.password.length < 8}
          variant="contained"
          sx={{ my: 2 }}
        >
          {t("submit")}
        </Button>
        <Box mt={3}>
          <Typography color={message.type === "error" ? "error" : "textPrimary"}>
            {message.text}
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

ResetPasswordForm.propTypes = {
  oobCode: PropTypes.string,
};
