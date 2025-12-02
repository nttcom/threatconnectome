import { Refresh } from "@mui/icons-material";
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

import { useAuth } from "../../hooks/auth";
import { useActionLock } from "../../hooks/useActionLock";
import { normalizeFullwidthDigits } from "../../utils/normalizeInput";

export function TwoFactorAuth(props) {
  const { authData, navigateInternalPage } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const [verificationId, setVerificationId] = useState(authData.verificationId);
  const [recaptchaResendKey, setRecaptchaResendKey] = useState(() => Date.now());
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });

  const { verifySmsForLogin, sendSmsCodeAgain } = useAuth();

  const { canExecute, timer, lockAction } = useActionLock(5);

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

    sendSmsCodeAgain(authData.phoneInfoOptions, authData.auth)
      .then((resendVerificationId) => {
        setVerificationId(resendVerificationId);
        setNotification({
          open: true,
          message: "The verification code has been resent.",
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

  return (
    <Box
      sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}
    >
      <Container maxWidth="xs">
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h6" gutterBottom>
              Two-factor authentication
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please enter the 6-digit code sent via SMS.
            </Typography>
          </Box>
          <Box component="form" onSubmit={handleVerify}>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Verification code"
                value={code}
                onChange={handleCodeChange}
                placeholder="123456"
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
                    Checking the code...
                  </>
                ) : (
                  "Authenticate"
                )}
              </Button>
              <Stack
                direction="row"
                spacing={1}
                sx={{ alignItems: "center", justifyContent: "center" }}
              >
                <Typography variant="body2" color="text.secondary">
                  Did you receive the code?
                </Typography>
                <Button
                  size="small"
                  disabled={!canExecute || isLoading}
                  onClick={handleResend}
                  sx={{ fontWeight: "bold" }}
                >
                  {canExecute ? (
                    <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
                      <Refresh fontSize="small" />
                      <span>Resend the code</span>
                    </Stack>
                  ) : (
                    `Resend in ${timer} seconds`
                  )}
                </Button>
                <div
                  id="recaptcha-container-invisible-resend"
                  key={recaptchaResendKey}
                  style={{ display: "none" }}
                />
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
