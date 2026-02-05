import CloseIcon from "@mui/icons-material/Close";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import {
  Alert,
  Box,
  Divider,
  IconButton,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../../../hooks/auth";
import { DeleteAccountDialog } from "../DeleteAccountDialog";

import { TwoFactorAuthSection } from "./TwoFactorAuthSection/TwoFactorAuthSection";

export function AccountSettingsDialog(props) {
  const { accountSettingOpen, setAccountSettingOpen, onUpdateUser, userMe } = props;
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const { isAuthenticatedWithSaml } = useAuth();
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.AccountSettingsDialog" });

  const handleShowSnackbar = (message, severity = "success") => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleClose = () => {
    setAccountSettingOpen(false);
  };

  return (
    <>
      <Dialog fullWidth maxWidth="sm" open={accountSettingOpen} onClose={handleClose}>
        <DialogTitle>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            {t("account")}
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                Email
              </Typography>
              <DialogContentText>{userMe.email}</DialogContentText>
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                User ID
              </Typography>
              <DialogContentText>{userMe.user_id}</DialogContentText>
            </Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Box>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                    Years of work experience in security
                  </Typography>
                  <Tooltip title="Please select years of your work experience in security to support security response.">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Select
                  size="small"
                  value={userMe.years}
                  onChange={(e) => {
                    onUpdateUser({ years: e.target.value });
                  }}
                  sx={{ minWidth: 130 }}
                >
                  <MenuItem value={0}>0+ year</MenuItem>
                  <MenuItem value={2}>2+ years</MenuItem>
                  <MenuItem value={5}>5+ years</MenuItem>
                  <MenuItem value={7}>7+ years</MenuItem>
                </Select>
              </Box>
            </Box>

            {import.meta.env.VITE_AUTH_SERVICE === "firebase" && !isAuthenticatedWithSaml() && (
              <TwoFactorAuthSection onShowSnackbar={handleShowSnackbar} />
            )}

            <Divider />
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                Team
              </Typography>
              <Stack spacing={1}>
                {userMe.pteam_roles.map((pteam_role) => (
                  <DialogContentText key={pteam_role.pteam.pteam_id}>
                    {pteam_role.pteam.pteam_name}
                  </DialogContentText>
                ))}
              </Stack>
            </Box>
            <Box>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                  Default Team
                </Typography>
                <Tooltip title="Your default team. This will be shown if no other team is currently selected.">
                  <IconButton size="small">
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Select
                size="small"
                value={userMe.default_pteam_id || "none"}
                onChange={(e) => {
                  onUpdateUser({
                    default_pteam_id: e.target.value === "none" ? null : e.target.value,
                  });
                }}
                sx={{ minWidth: 200 }}
                displayEmpty
              >
                <MenuItem value="none">
                  <em>None</em>
                </MenuItem>
                {userMe.pteam_roles.map((pteam_role) => (
                  <MenuItem key={pteam_role.pteam.pteam_id} value={pteam_role.pteam.pteam_id}>
                    {pteam_role.pteam.pteam_name}
                  </MenuItem>
                ))}
              </Select>
            </Box>

            <Box>
              <DeleteAccountDialog userMe={userMe} />
            </Box>
          </Stack>
        </DialogContent>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert onClose={handleSnackbarClose} severity={snackbar.severity} variant="filled">
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Dialog>
    </>
  );
}
AccountSettingsDialog.propTypes = {
  accountSettingOpen: PropTypes.bool.isRequired,
  setAccountSettingOpen: PropTypes.func.isRequired,
  onUpdateUser: PropTypes.func.isRequired,
  userMe: PropTypes.object.isRequired,
};
