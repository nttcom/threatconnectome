import { WarningAmber } from "@mui/icons-material";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../../../../hooks/auth";
import { maskPhoneNumber } from "../../../../../utils/phoneNumberUtils";

export function DisabledMfaConfirmDialog({ open, onClose, onConfirm }) {
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.DisabledMfaConfirmDialog" });
  const dialogTitleId = "disable-mfa-dialog-title";
  const dialogDescriptionId = "disable-mfa-dialog-description";

  const { getPhoneNumber } = useAuth();

  const phoneNumber = getPhoneNumber();
  const modifiedPhoneNumber = phoneNumber ? maskPhoneNumber(phoneNumber) : "N/A";

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      aria-labelledby={dialogTitleId}
      aria-describedby={dialogDescriptionId}
    >
      <DialogTitle
        id={dialogTitleId}
        sx={{ display: "flex", alignItems: "center", gap: 1, color: "text.primary" }}
      >
        <WarningAmber color="warning" />
        {t("title", { phoneNumber: modifiedPhoneNumber })}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id={dialogDescriptionId} gutterBottom>
          {t("warning")}
        </DialogContentText>
        <DialogContentText variant="body2" color="text.secondary">
          {t("note")}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          {t("cancel")}
        </Button>
        <Button onClick={onConfirm} color="warning" variant="contained">
          {t("disable")}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

DisabledMfaConfirmDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
};
