import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { SmsResendButton } from "../../components/SmsResendButton";
import { SmsTroubleshootingTips } from "../../components/SmsTroubleshootingTips";
import { SmsTroubleshootingToggleButton } from "../../components/SmsTroubleshootingToggleButton";
import { useAuth } from "../../hooks/auth";
import { useActionLock } from "../../hooks/useActionLock";
import { normalizeFullwidthDigits } from "../../utils/normalizeInput";

export function TwoFactorAuth(props) {
  const { t } = useTranslation("login", { keyPrefix: "TwoFactorAuth" });
  const { authData, navigateInternalPage } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const [verificationId, setVerificationId] = useState(authData.verificationId);
  const [recaptchaResendKey, setRecaptchaResendKey] = useState(() => Date.now());
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });
  const [isHelpExpanded, setIsHelpExpanded] = useState(false);

  const { verifySmsForLogin, sendSmsCodeAgain } = useAuth();

  const { canExecute, timer, lockAction } = useActionLock(5);

  const recaptchaId = "recaptcha-container-invisible-resend";

  const handleCodeChange = (e) => {
    const normalized = normalizeFullwidthDigits(e.target.value);
    const sanitized = normalized.replace(/\D/g, "").slice(0, 6);
    setCode(sanitized);
    if (codeError) {
      setCodeError(null);
    }
  };

  const handleVerify = (e) => {
    e.preventDefault();
    setCodeError(null);
    verifySmsForLogin(authData.resolver, verificationId, code)
      .then(() => {
        setIsLoading(true);
        navigateInternalPage();
      })
      .catch((error) => {
        setCodeError(error.message);
      });
  };

  const handleResend = async () => {
    lockAction();

    sendSmsCodeAgain(authData.phoneInfoOptions, authData.auth, recaptchaId)
      .then((resendVerificationId) => {
        setVerificationId(resendVerificationId);
        setNotification({
          open: true,
          message: t("codeResent"),
          type: "info",
        });
        setRecaptchaResendKey(Date.now()); // Force re-mount recaptcha for resend
      })
      .catch((error) => {
        setCodeError(error.message);
      });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const handleToggleHelp = () => {
    setIsHelpExpanded((prev) => !prev);
  };

  return (
    <Box
      sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}
    >
      <Container maxWidth="xs">
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h6" gutterBottom>
              {t("title")}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t("subtitle")}
            </Typography>
          </Box>
          <Box component="form" onSubmit={handleVerify}>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label={t("verificationCodeLabel")}
                value={code}
                onChange={handleCodeChange}
                placeholder={t("verificationCodePlaceholder")}
                slotProps={{
                  htmlInput: {
                    inputMode: "numeric",
                    maxLength: 6,
                    "aria-label": "Verification code input",
                    style: {
                      textAlign: "center",
                      letterSpacing: "0.5em",
                    },
                  },
                }}
                error={Boolean(codeError)}
                helperText={codeError}
              />
              <Button
                variant="contained"
                fullWidth
                disabled={code.length !== 6 || isLoading}
                type="submit"
              >
                {isLoading ? (
                  <>
                    <CircularProgress size={18} sx={{ mr: 1 }} />
                    {t("checkingCode")}
                  </>
                ) : (
                  t("authenticate")
                )}
              </Button>
              <Stack spacing={1.5} sx={{ alignItems: "flex-start", width: "100%" }}>
                <Typography variant="body2" color="text.secondary">
                  {t("didYouReceive")}
                </Typography>
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{
                    alignItems: "center",
                    flexWrap: "wrap",
                    justifyContent: "flex-start",
                    rowGap: 1,
                    width: "100%",
                  }}
                >
                  <SmsResendButton
                    canExecute={canExecute}
                    isBusy={isLoading}
                    timer={timer}
                    onResend={handleResend}
                  />
                  <SmsTroubleshootingToggleButton
                    expanded={isHelpExpanded}
                    onToggle={handleToggleHelp}
                    disabled={isLoading}
                  />
                </Stack>
                {isHelpExpanded && <SmsTroubleshootingTips />}
                <div id={recaptchaId} key={recaptchaResendKey} style={{ display: "none" }} />
              </Stack>
            </Stack>
          </Box>
          <Snackbar
            open={notification.open}
            autoHideDuration={4000}
            onClose={handleCloseNotification}
            anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          >
            <Alert severity={notification.type} variant="filled">
              {notification.message}
            </Alert>
          </Snackbar>
        </Paper>
      </Container>
    </Box>
  );
}

TwoFactorAuth.propTypes = {
  authData: PropTypes.object.isRequired,
  navigateInternalPage: PropTypes.func.isRequired,
};
