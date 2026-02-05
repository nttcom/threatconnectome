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
import { useTranslation } from "react-i18next";

import { SmsResendButton } from "../../../../../components/SmsResendButton";
import { SmsTroubleshootingTips } from "../../../../../components/SmsTroubleshootingTips";
import { SmsTroubleshootingToggleButton } from "../../../../../components/SmsTroubleshootingToggleButton";
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

export function MfaSetupDialog({ open, onClose, onSuccess }) {
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.MfaSetupDialog" });
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
          message: t("codeResent"),
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
      <DialogTitle>{step === 0 ? t("titleSetup") : t("titleVerify")}</DialogTitle>
      <DialogContent>
        {step === 0 ? (
          <>
            <DialogContentText sx={{ mb: 2 }}>{t("enterPhoneNumber")}</DialogContentText>

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
                label={t("phoneNumber")}
                type="tel"
                fullWidth
                variant="outlined"
                value={phoneNumber}
                onChange={handlePhoneNumberChange}
                placeholder={t("phonePlaceholder")}
                disabled={loading}
                error={!!error}
                helperText={error}
              />
            </Stack>
          </>
        ) : (
          <>
            <DialogContentText sx={{ mb: 2 }}>
              {t("codeSentTo", { countryCode, phoneNumber })}
            </DialogContentText>
            <TextField
              label={t("verificationCode")}
              fullWidth
              variant="outlined"
              value={verificationCode}
              onChange={handleCodeChange}
              disabled={loading}
              error={!!error}
              helperText={error}
              placeholder={t("codePlaceholder")}
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
                    isBusy={loading}
                    timer={timer}
                    onResend={handleResend}
                  />
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
                    {t("changePhoneNumber")}
                  </Button>
                  <SmsTroubleshootingToggleButton
                    expanded={isHelpExpanded}
                    onToggle={handleToggleHelp}
                    disabled={loading}
                  />
                </Stack>
                {isHelpExpanded && <SmsTroubleshootingTips />}
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
          {t("cancel")}
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
                {loading ? t("processing") : t("sendCode")}
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
            {loading ? t("processing") : t("verifyEnable")}
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
