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

import { useAuth } from "../../hooks/auth";

export function TwoFactorAuth(props) {
  const { authData, navigateInternalPage } = props;

  const [step, setStep] = useState("2fa");
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const [canResend, setCanResend] = useState(true);
  const [timer, setTimer] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });
  const [verificationId, setVerificationId] = useState(authData[1]);

  const { verifySmsForLogin, sendSmsCodeAgain } = useAuth();

  useEffect(() => {
    let interval = null;
    if (timer > 0) {
      interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
    } else {
      setCanResend(true);
    }
    return () => clearInterval(interval);
  }, [timer]);

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
    verifySmsForLogin(authData[0], verificationId, code)
      .then(() => {
        setStep("loading");
        navigateInternalPage();
      })
      .catch((error) => {
        if (error.code === "auth/invalid-verification-code") {
          setCodeError("コードが正しくありません。もう一度お試しください。");
        } else {
          setCodeError(error);
        }
      });
  };

  const handleResend = async () => {
    const resendVerificationId = await sendSmsCodeAgain(authData[2], authData[3]);
    setVerificationId(resendVerificationId);
    setTimer(5);
    setCanResend(false);
    setNotification({ open: true, message: "認証コードを再送信しました。", type: "info" });
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
              二要素認証
            </Typography>
            <Typography variant="body2" color="text.secondary">
              "SMSで送信された6桁のコードを入力してください"
            </Typography>
          </Box>

          {(step === "2fa" || step === "loading") && (
            <>
              <Box component="form" onSubmit={handleVerify}>
                <Stack spacing={2}>
                  <TextField
                    fullWidth
                    label="認証コード"
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
                    disabled={code.length !== 6 || step === "loading"}
                    type="submit"
                  >
                    {step === "loading" ? (
                      <>
                        <CircularProgress size={18} sx={{ mr: 1 }} />
                        コードを確認しています...
                      </>
                    ) : (
                      "認証する"
                    )}
                  </Button>
                  <Stack
                    direction="row"
                    spacing={1}
                    sx={{ alignItems: "center", justifyContent: "center" }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      コードが届きませんか？
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
                          <span>コードを再送信</span>
                        </Stack>
                      ) : (
                        `再送信まで ${timer}秒`
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
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
}
