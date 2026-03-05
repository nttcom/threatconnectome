import { Box, Button, Typography, Container, CircularProgress } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { PasswordField } from "../../components/PasswordField";
import { useAuth } from "../../hooks/auth";

export default function ResetPasswordForm(props) {
  const { t } = useTranslation("emailVerification", { keyPrefix: "ResetPasswordForm" });
  const { oobCode } = props;
  const [disabled, setDisabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" }); // type: 'info' | 'error'
  const [resetForm, setResetForm] = useState({
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
    if (resetForm.password !== resetForm.confirmPassword) {
      showMessage(t("passwordsDoNotMatch"));
      return;
    }

    setDisabled(true);
    setIsLoading(true);

    await verifyPasswordResetCode({ actionCode: oobCode })
      .then(() => {
        confirmPasswordReset({ actionCode: oobCode, newPassword: resetForm.password });
      })
      .then(() => {
        showMessage(t("success"), "info");
      })
      .catch((error) => {
        console.error(error);
        showMessage(error.message);
        setDisabled(false);
      });
    setIsLoading(false);
  }

  const handleVisibility = (prop) => {
    setResetForm((prev) => ({ ...prev, [prop]: !prev[prop] }));
  };

  const handleFormChange = (prop) => (event) => {
    resetForm.edited.add(prop);
    setResetForm({
      ...resetForm,
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
          value={resetForm.password}
          edited={resetForm.edited}
          onChange={handleFormChange("password")}
          isVisible={resetForm.isVisible}
          onToggle={() => handleVisibility("isVisible")}
          tooltipTitle={t("passwordHint")}
        />
        <PasswordField
          name="confirmPassword"
          label={t("confirmPassword")}
          value={resetForm.confirmPassword}
          edited={resetForm.edited}
          onChange={handleFormChange("confirmPassword")}
          isVisible={resetForm.isConfirmVisible}
          onToggle={() => handleVisibility("isConfirmVisible")}
          tooltipTitle={t("passwordHint")}
        />
        <Button
          onClick={() => handleResetPassword()}
          disabled={
            disabled || resetForm.password.length < 8 || resetForm.confirmPassword.length < 8
          }
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
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
