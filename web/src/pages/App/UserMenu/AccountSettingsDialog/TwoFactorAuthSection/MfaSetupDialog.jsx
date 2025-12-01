import { Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  fabClasses,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";

import { useAuth } from "../../../../../hooks/auth";
import { useSmsResend } from "../../../../../hooks/useSmsResend";
import { normalizeFullwidthDigits } from "../../../../../utils/normalizeInput";

const COUNTRY_CODES = [
  { code: "+81", label: "JP (+81)" },
  { code: "+1", label: "US (+1)" },
  { code: "+44", label: "UK (+44)" },
  { code: "+86", label: "CN (+86)" },
  { code: "+82", label: "KR (+82)" },
];

export function MfaSetupDialog({ open, onClose, onSuccess }) {
  const [step, setStep] = useState(0);
  const [countryCode, setCountryCode] = useState("+81");
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [authData, setAuthData] = useState(null);
  const [isRecaptchaVisible, setIsRecaptchaVisible] = useState(false);
  const [recaptchaResendKey, setRecaptchaResendKey] = useState(() => Date.now());

  const { registerPhoneNumber, verifySmsForEnrollment, sendSmsCodeAgain } = useAuth();

  const {
    canResend,
    timer,
    notification,
    startResendTimer,
    resetResendState,
    showNotification,
    closeNotification,
  } = useSmsResend(5);

  useEffect(() => {
    const recaptcha_element = document.getElementById(
      "recaptcha-container-visible-register-phone-number",
    );
    if (!recaptcha_element) return;

    const check = () => {
      setIsRecaptchaVisible(recaptcha_element.childElementCount > 0);
    };

    check();
    const observer = new MutationObserver(check);
    observer.observe(recaptcha_element, { childList: true });
    return () => observer.disconnect();
  }, [loading]);

  const resetState = () => {
    setStep(0);
    setCountryCode("+81");
    setPhoneNumber("");
    setCode("");
    setError("");
    resetResendState();
    setIsRecaptchaVisible(false);
  };

  const handleClose = () => {
    if (loading) return;
    onClose();
  };

  const handleSendCode = async () => {
    setLoading(true);
    setError("");
    resetResendState();
    registerPhoneNumber(countryCode + phoneNumber)
      .then((auth) => {
        setAuthData(auth);
        setLoading(false);
        setStep(1);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleVerifyCode = () => {
    setLoading(true);
    setError("");
    verifySmsForEnrollment(authData.verificationId, code)
      .then(() => {
        onSuccess();
        handleClose();
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleCodeChange = (e) => {
    const normalized = normalizeFullwidthDigits(e.target.value);
    const sanitized = normalized.replace(/\D/g, "").slice(0, 6);
    setCode(sanitized);
    if (error) {
      setError("");
    }
  };

  const handlePhoneNumberChange = (e) => {
    const normalized = normalizeFullwidthDigits(e.target.value);
    const sanitized = normalized.replace(/\D/g, "");
    setPhoneNumber(sanitized);
    if (error) {
      setError("");
    }
  };

  const handleResend = () => {
    setLoading(true);
    startResendTimer();
    setError("");
    sendSmsCodeAgain(authData.phoneInfoOptions, authData.auth)
      .then((resendVerificationId) => {
        setAuthData((prevAuthData) => ({
          ...prevAuthData,
          verificationId: resendVerificationId,
        }));
        setLoading(false);
        showNotification("The verification code has been resent.", "info");
        setRecaptchaResendKey(Date.now()); // Force re-mount recaptcha for resend
      })
      .catch((error) => {
        console.log("handleResend: error");
        console.log(error);
        console.log(error.message);
        setError(error.message);
        setLoading(false);
      });
  };

  const handleCloseNotification = () => {
    closeNotification();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xs"
      fullWidth
      slotProps={{ transition: { onExited: resetState } }}
    >
      <DialogTitle>
        {step === 0 ? "Setup SMS Authentication" : "Enter Verification Code"}
      </DialogTitle>
      <DialogContent>
        {step === 0 ? (
          <>
            <DialogContentText sx={{ mb: 2 }}>
              Please enter your mobile phone number to enable 2FA
            </DialogContentText>

            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Select
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value)}
                disabled={loading}
                variant="outlined"
                sx={{ width: 130 }}
                renderValue={(value) => value} // Show only the code when selected to keep it compact
              >
                {COUNTRY_CODES.map((option) => (
                  <MenuItem key={option.code} value={option.code}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
              <TextField
                label="Phone Number"
                type="tel"
                fullWidth
                variant="outlined"
                value={phoneNumber}
                onChange={handlePhoneNumberChange}
                placeholder="9012345678"
                disabled={loading}
                error={!!error}
                helperText={error}
              />
            </Stack>
          </>
        ) : (
          <>
            <DialogContentText sx={{ mb: 2 }}>
              We sent a 6-digit verification code to{" "}
              <b>
                {countryCode} {phoneNumber}
              </b>
            </DialogContentText>
            <TextField
              label="Verification Code"
              fullWidth
              variant="outlined"
              value={code}
              onChange={handleCodeChange}
              disabled={loading}
              error={!!error}
              helperText={error}
              placeholder="123456"
              slotProps={{
                htmlInput: {
                  maxLength: 6,
                  inputMode: "numeric",
                  pattern: "[0-9]*",
                  "aria-label": "6-digit verification code input",
                  style: { letterSpacing: "0.2em", textAlign: "center" },
                },
              }}
            />
            <Stack spacing={2} sx={{ mt: 2, alignItems: "center" }}>
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
                  disabled={!canResend || loading}
                  onClick={handleResend}
                  sx={{ fontWeight: "bold" }}
                >
                  {canResend ? (
                    <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
                      <Refresh fontSize="small" />
                      <span>Resend Code</span>
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
              <Button
                size="small"
                onClick={() => {
                  setStep(0);
                  setIsRecaptchaVisible(false);
                }}
                disabled={loading}
              >
                Change Phone Number
              </Button>
            </Stack>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        {step === 0 && (
          <>
            <Box
              id="recaptcha-container-visible-register-phone-number"
              sx={{
                mt: isRecaptchaVisible ? 2 : 0,
                mb: isRecaptchaVisible ? 2 : 0,
                display: "flex",
                justifyContent: "center",
              }}
            />
            {!isRecaptchaVisible && (
              <Button
                onClick={handleSendCode}
                variant="contained"
                disabled={loading || !phoneNumber}
              >
                {loading ? "Processing..." : "Send Code"}
              </Button>
            )}
          </>
        )}
        {step === 1 && (
          <Button
            onClick={handleVerifyCode}
            variant="contained"
            disabled={loading || !(code.length === 6)}
          >
            {loading ? "Processing..." : "Verify & Enable"}
          </Button>
        )}
      </DialogActions>
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
    </Dialog>
  );
}

MfaSetupDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};
