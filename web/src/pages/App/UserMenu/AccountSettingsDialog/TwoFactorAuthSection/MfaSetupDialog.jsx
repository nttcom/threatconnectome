import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

const COUNTRY_CODES = [
  { code: "+81", label: "JP (+81)" },
  { code: "+1", label: "US (+1)" },
  { code: "+44", label: "UK (+44)" },
  { code: "+86", label: "CN (+86)" },
  { code: "+82", label: "KR (+82)" },
];

const DEMO_CORRECT_CODE = "123456";

export function MfaSetupDialog({ open, onClose, onSuccess }) {
  const [step, setStep] = useState(0);
  const [countryCode, setCountryCode] = useState("+81");
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const handleClose = () => {
    if (loading) return;
    onClose();
    // Reset state after dialog is closed
    setTimeout(() => {
      setStep(0);
      setCountryCode("+81");
      setPhoneNumber("");
      setCode("");
      setError("");
    }, 200);
  };

  const handleSendCode = () => {
    setLoading(true);
    setError("");
    setCode("");
    setTimeout(() => {
      setLoading(false);
      setStep(1);
    }, 1500);
  };

  const handleVerifyCode = () => {
    if (code === DEMO_CORRECT_CODE) {
      setLoading(true);
      setError("");
      setTimeout(() => {
        onSuccess();
        setLoading(false);
        handleClose();
      }, 1500);
    } else {
      setLoading(true);
      setTimeout(() => {
        setError("Invalid verification code. Please try again.");
        setLoading(false);
      }, 1500);
    }
  };

  const handleCodeChange = (e) => {
    const val = e.target.value;
    if (/^\d*$/.test(val)) {
      setCode(val);
      if (error) {
        setError("");
      }
    }
  };

  const handlePhoneNumberChange = (e) => {
    const val = e.target.value;
    if (/^\d*$/.test(val)) {
      setPhoneNumber(val);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
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
                    {option.code}
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
              placeholder={DEMO_CORRECT_CODE}
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
            <Button size="small" onClick={() => setStep(0)} disabled={loading} sx={{ mt: 2 }}>
              Change Phone Number
            </Button>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={step === 0 ? handleSendCode : handleVerifyCode}
          variant="contained"
          disabled={loading || (step === 0 ? !phoneNumber : !(code.length === 6))}
        >
          {loading ? "Processing..." : step === 0 ? "Send Code" : "Verify & Enable"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

MfaSetupDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};
