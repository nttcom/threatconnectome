import {
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

export function TwoFactorAuth() {
  const [step, setStep] = useState("2fa");
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(null);
  const handleCodeChange = (e) => {
    setCode(e.target.value);
    console.log(e.target.value);
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
              </Stack>
            </Box>
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
