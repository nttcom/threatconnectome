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

export function DisabledMfaConfirmDialog({ open, onClose, onConfirm }) {
  const dialogTitleId = "disable-mfa-dialog-title";
  const dialogDescriptionId = "disable-mfa-dialog-description";

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
        Disable SMS Authentication?
      </DialogTitle>
      <DialogContent>
        <DialogContentText id={dialogDescriptionId} gutterBottom>
          By disabling SMS Authentication, your account will be only protected by your password.
        </DialogContentText>
        <DialogContentText variant="body2" color="text.secondary">
          Note: To change your phone number, disable SMS Authentication first and then set it up
          again.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>
        <Button onClick={onConfirm} color="warning" variant="contained">
          Disable
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
