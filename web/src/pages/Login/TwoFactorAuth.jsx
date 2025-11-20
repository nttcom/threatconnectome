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

export function TwoFactorAuth() {
  const [step, setStep] = useState("2fa");
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const [canResend, setCanResend] = useState(true);
  const [timer, setTimer] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });

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
    const MOCK_VALID_CODE = "123456";
    setCodeError(null);
    setStep("loading");
    setTimeout(() => {
      if (code === MOCK_VALID_CODE) {
        setStep("main");
      } else {
        setCodeError("コードが正しくありません。もう一度お試しください。");
        setStep("2fa");
      }
    }, 1000);
  };

  const handleResend = () => {
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
              {step === "main" ? "ログイン完了" : "二要素認証"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {(step === "2fa" || step === "loading") &&
                "SMSで送信された6桁のコードを入力してください"}
              {step === "main" && "認証に成功しました。"}
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

          {step === "main" && (
            <Box>
              <Typography variant="body2" gutterBottom>
                認証に成功しました。実際のアプリケーションでは、このあとメイン画面に遷移させてください。
              </Typography>
              <Button
                variant="contained"
                size="small"
                onClick={() => {
                  setCode("");
                  setCodeError(null);
                  setStep("2fa");
                  setCanResend(false);
                  setTimer(0);
                }}
              >
                もう一度試す
              </Button>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
}
