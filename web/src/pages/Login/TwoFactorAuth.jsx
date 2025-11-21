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
import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { useAuth } from "../../hooks/auth";

export function TwoFactorAuth(props) {
  const { authData, navigateInternalPage } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const [canResend, setCanResend] = useState(true);
  const [timer, setTimer] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });
  const [verificationId, setVerificationId] = useState(authData.verificationId);

  const { verifySmsForLogin, sendSmsCodeAgain } = useAuth();

  useEffect(() => {
    if (!canResend && timer > 0) {
      let interval = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [canResend]);

  const handleCodeChange = (e) => {
    const sanitized = e.target.value.replace(/\D/g, "").slice(0, 6);
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
        if (error.code === "auth/invalid-verification-code") {
          setCodeError("The code is incorrect. Please try again.");
        } else {
          setCodeError(error);
        }
      });
  };

  const handleResend = async () => {
    const resendVerificationId = await sendSmsCodeAgain(authData.phoneInfoOptions, authData.auth);
    setVerificationId(resendVerificationId);
    setTimer(5);
    setCanResend(false);
    setNotification({
      open: true,
      message: "The authentication code has been resent.",
      type: "info",
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
                label="Authentication code"
                value={code}
                onChange={handleCodeChange}
                placeholder="123456"
                slotProps={{
                  htmlInput: {
                    inputMode: "numeric",
                    maxLength: 6,
                    "aria-label": "Authentication code input",
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
                  id="recaptcha-container-invisible-resend"
                  size="small"
                  disabled={!canResend}
                  onClick={handleResend}
                  sx={{ fontWeight: "bold" }}
                >
                  {canResend ? (
                    <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
                      <Refresh fontSize="small" />
                      <span>Resend the code</span>
                    </Stack>
                  ) : (
                    `Resend in ${timer} seconds`
                  )}
                </Button>
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
