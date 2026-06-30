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
import type { AlertColor, SelectChangeEvent } from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../../../hooks/auth";
import { getExperienceBucket } from "../../../../utils/const";
import type { UserResponse, UserUpdateRequest } from "../../../../../types/types.gen";
import { DeleteAccountDialog } from "../DeleteAccountDialog";

import { TwoFactorAuthSection } from "./TwoFactorAuthSection/TwoFactorAuthSection";

type AccountSettingsDialogProps = {
  accountSettingOpen: boolean;
  setAccountSettingOpen: (open: boolean) => void;
  onUpdateUser: (request: UserUpdateRequest) => void | Promise<void>;
  userMe: UserResponse;
};

type SnackbarState = {
  open: boolean;
  message: string;
  severity: AlertColor;
};

export function AccountSettingsDialog({
  accountSettingOpen,
  setAccountSettingOpen,
  onUpdateUser,
  userMe,
}: AccountSettingsDialogProps) {
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: "",
    severity: "success",
  });

  const { isAuthenticatedWithSaml } = useAuth();
  const { t } = useTranslation("app", {
    keyPrefix: "UserMenu.AccountSettingsDialog.AccountSettingsDialog",
  });

  const handleShowSnackbar = (message: string, severity: AlertColor = "success") => {
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
                {t("email")}
              </Typography>
              <DialogContentText>{userMe.email}</DialogContentText>
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                {t("userId")}
              </Typography>
              <DialogContentText>{userMe.user_id}</DialogContentText>
            </Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <Box>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                    {t("yearsOfExperience")}
                  </Typography>
                  <Tooltip title={t("yearsTooltip")}>
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Select
                  size="small"
                  value={getExperienceBucket(userMe.years)}
                  onChange={(e) => {
                    onUpdateUser({ years: Number(e.target.value) });
                  }}
                  sx={{ minWidth: 130 }}
                >
                  <MenuItem value={0}>{t("years0")}</MenuItem>
                  <MenuItem value={2}>{t("years2")}</MenuItem>
                  <MenuItem value={5}>{t("years5")}</MenuItem>
                  <MenuItem value={7}>{t("years7")}</MenuItem>
                </Select>
              </Box>
            </Box>

            {import.meta.env.VITE_AUTH_SERVICE === "firebase" && !isAuthenticatedWithSaml() && (
              <TwoFactorAuthSection onShowSnackbar={handleShowSnackbar} />
            )}

            <Divider />
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                {t("team")}
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
                  {t("defaultTeam")}
                </Typography>
                <Tooltip title={t("defaultTeamTooltip")}>
                  <IconButton size="small">
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Select
                size="small"
                value={userMe.default_pteam_id || "none"}
                onChange={(e: SelectChangeEvent) => {
                  onUpdateUser({
                    default_pteam_id: e.target.value === "none" ? null : e.target.value,
                  });
                }}
                sx={{ minWidth: 200 }}
                displayEmpty
              >
                <MenuItem value="none">
                  <em>{t("none")}</em>
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
