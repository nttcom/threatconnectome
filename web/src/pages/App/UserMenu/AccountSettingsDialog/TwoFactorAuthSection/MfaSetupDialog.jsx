import { ExpandLess, ExpandMore, Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
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
import { useActionLock } from "../../../../../hooks/useActionLock";
import { normalizeFullwidthDigits } from "../../../../../utils/normalizeInput";

const COUNTRY_CODES = [
  { code: "+81", label: "JP (+81)" },
  { code: "+1", label: "US (+1)" },
  { code: "+44", label: "UK (+44)" },
  { code: "+86", label: "CN (+86)" },
  { code: "+82", label: "KR (+82)" },
];

const TROUBLESHOOTING_TIPS = [
  "The phone number entered is accurate.",
  "Your device has sufficient network coverage and is not in airplane mode.",
  "SMS filtering, blocking settings, or carrier restrictions are not preventing delivery.",
  "The message has not been placed in your spam or junk folder.",
];

export function MfaSetupDialog({ open, onClose, onSuccess }) {
  const [step, setStep] = useState(0);
  const [countryCode, setCountryCode] = useState("+81");
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [error, setError] = useState("");
  const [mfaData, setMfaData] = useState(null);
  const [isRecaptchaVisible, setIsRecaptchaVisible] = useState(false);
  const [recaptchaResendKey, setRecaptchaResendKey] = useState(() => Date.now());
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });
  const [isHelpExpanded, setIsHelpExpanded] = useState(false);

  const { registerPhoneNumber, verifySmsForEnrollment, sendSmsCodeAgain } = useAuth();

  const { canExecute, timer, lockAction, unlockAction } = useActionLock(5);

  const recaptchaIdForRegisterPhoneNumber = "recaptcha-container-visible-register-phone-number";
  const recaptchaIdForResend = "recaptcha-container-invisible-resend";

  useEffect(() => {
    const recaptcha_element = document.getElementById(recaptchaIdForRegisterPhoneNumber);
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
    setVerificationCode("");
    setError("");
    unlockAction();
    setIsRecaptchaVisible(false);
    setIsHelpExpanded(false);
  };

  const handleClose = () => {
    if (loading) return;
    onClose();
  };

  const handleSendCode = async () => {
    setLoading(true);
    setError("");
    unlockAction();
    registerPhoneNumber(countryCode + phoneNumber, recaptchaIdForRegisterPhoneNumber)
      .then((mfa) => {
        setMfaData(mfa);
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
    verifySmsForEnrollment(mfaData.verificationId, verificationCode)
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
    setVerificationCode(sanitized);
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
    lockAction();
    setError("");
    sendSmsCodeAgain(mfaData.phoneInfoOptions, mfaData.auth, recaptchaIdForResend)
      .then((resendVerificationId) => {
        setMfaData((prevMfaData) => ({
          ...prevMfaData,
          verificationId: resendVerificationId,
        }));
        setLoading(false);
        setNotification({
          open: true,
          message: "The verification code has been resent.",
          type: "info",
        });
        setRecaptchaResendKey(Date.now()); // Force re-mount recaptcha for resend
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const handleToggleHelp = () => {
    setIsHelpExpanded((prev) => !prev);
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
              value={verificationCode}
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
            <Stack spacing={2} sx={{ mt: 2, alignItems: "flex-start", width: "100%" }}>
              <Stack spacing={1} sx={{ alignItems: "flex-start", width: "100%" }}>
                <Typography variant="body2" color="text.secondary">
                  Did you receive the code?
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
                  <Button
                    size="small"
                    disabled={!canExecute || loading}
                    onClick={handleResend}
                    sx={{ fontWeight: "bold" }}
                  >
                    {canExecute ? (
                      <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
                        <Refresh fontSize="small" />
                        <span>Resend Code</span>
                      </Stack>
                    ) : (
                      `Resend in ${timer} seconds`
                    )}
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    onClick={() => {
                      setStep(0);
                      setIsRecaptchaVisible(false);
                      setIsHelpExpanded(false);
                    }}
                    disabled={loading}
                  >
                    Change Phone Number
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    onClick={handleToggleHelp}
                    disabled={loading}
                    sx={{
                      minWidth: 0,
                      p: 0,
                      textTransform: "none",
                      alignItems: "center",
                      display: "inline-flex",
                      flexBasis: "100%",
                      justifyContent: "flex-start",
                      "& .MuiButton-startIcon": { marginRight: 0.5 },
                    }}
                    startIcon={
                      isHelpExpanded ? (
                        <ExpandLess fontSize="small" />
                      ) : (
                        <ExpandMore fontSize="small" />
                      )
                    }
                  >
                    {isHelpExpanded ? "Hide troubleshooting tips" : "View troubleshooting tips"}
                  </Button>
                </Stack>
                {isHelpExpanded && (
                  <Box
                    sx={{
                      width: "100%",
                      mt: 1,
                      pl: 1,
                    }}
                  >
                    <Typography variant="body2" sx={{ ml: 0.5, fontWeight: 600 }} gutterBottom>
                      If the verification SMS does not arrive, please verify the following:
                    </Typography>
                    <Box
                      component="ol"
                      sx={{ pl: 4, m: 0, fontSize: (theme) => theme.typography.body2.fontSize }}
                    >
                      {TROUBLESHOOTING_TIPS.map((tip) => (
                        <Box component="li" key={tip} sx={{ mb: 0.5 }}>
                          {tip}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
                <div
                  id={recaptchaIdForResend}
                  key={recaptchaResendKey}
                  style={{ display: "none" }}
                />
              </Stack>
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
              id={recaptchaIdForRegisterPhoneNumber}
              sx={{
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
            disabled={loading || !(verificationCode.length === 6)}
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
