import { Box, Switch, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { useAuth } from "../../../../../hooks/auth";

import { DisabledMfaConfirmDialog } from "./DisabledMfaConfirmDialog";
import { MfaSetupDialog } from "./MfaSetupDialog";


export function TwoFactorAuthSection({ onShowSnackbar }) {
  const { deletePhoneNumber, isSmsAuthenticationEnabled } = useAuth();

  const [isEnabled, setIsEnabled] = useState(isSmsAuthenticationEnabled());
  const [setupOpen, setSetupOpen] = useState(false);
  const [disableConfirmOpen, setDisableConfirmOpen] = useState(false);

  const handleToggleTwoFactor = (event) => {
    if (event.target.checked) {
      setSetupOpen(true);
    } else {
      setDisableConfirmOpen(true);
    }
  };

  const handleSuccess = () => {
    setIsEnabled(true);
    onShowSnackbar("SMS authentication enabled successfully!", "success");
  };

  const handleDisableConfirm = () => {
    deletePhoneNumber()
      .then(() => {
        setIsEnabled(false);
        setDisableConfirmOpen(false);
        onShowSnackbar("SMS authentication disabled.", "info");
      })
      .catch((error) => {
        onShowSnackbar(error.message, "error");
      });
  };

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
        Two-factor Authentication
      </Typography>

      <Box sx={{ mt: 1, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Box>
          <Typography variant="body1">SMS Authentication</Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            {isEnabled
              ? "Enabled. Code required at login."
              : "Protect your account with SMS verification."}
          </Typography>
        </Box>
        <Switch checked={isEnabled} onChange={handleToggleTwoFactor} color="primary" edge="end" />
      </Box>

      <MfaSetupDialog
        open={setupOpen}
        onClose={() => setSetupOpen(false)}
        onSuccess={handleSuccess}
      />

      <DisabledMfaConfirmDialog
        open={disableConfirmOpen}
        onClose={() => setDisableConfirmOpen(false)}
        onConfirm={handleDisableConfirm}
      />
    </Box>
  );
}

TwoFactorAuthSection.propTypes = {
  onShowSnackbar: PropTypes.func.isRequired,
};
