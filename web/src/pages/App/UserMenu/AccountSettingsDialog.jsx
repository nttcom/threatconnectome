import CloseIcon from "@mui/icons-material/Close";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { Box, IconButton, MenuItem, Select, Stack, Tooltip, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import React from "react";

import { DeleteAccountDialog } from "./DeleteAccountDialog";

export function AccountSettingsDialog(props) {
  const { accountSettingOpen, setAccountSettingOpen, onSelectYear, userMe } = props;

  const handleClose = () => {
    setAccountSettingOpen(false);
  };

  // Change Email is not implemented
  const changeEmaildisabled = true;
  // Change Password is not implemented
  const changePasswordDisabled = true;

  return (
    <>
      <Dialog fullWidth maxWidth="sm" open={accountSettingOpen} onClose={handleClose}>
        <DialogTitle>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            Account settings
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
              <Button
                variant="contained"
                size="small"
                sx={{ mt: 1 }}
                disabled={changeEmaildisabled}
              >
                Change Email
              </Button>
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                User ID
              </Typography>
              <DialogContentText>{userMe.user_id}</DialogContentText>
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                Password
              </Typography>
              <Button variant="contained" size="small" disabled={changePasswordDisabled}>
                Change Password
              </Button>
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                Team
              </Typography>
              {userMe.pteam_roles.map((pteam_role) => (
                <>
                  <DialogContentText>{pteam_role.pteam.pteam_name}</DialogContentText>
                  <DialogContentText variant="caption">
                    {pteam_role.pteam.pteam_id}
                  </DialogContentText>
                </>
              ))}
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
                  defaultValue={userMe.years}
                  onChange={(e) => {
                    onSelectYear(e);
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
            <Box>
              <DeleteAccountDialog />
            </Box>
          </Stack>
        </DialogContent>
      </Dialog>
    </>
  );
}
AccountSettingsDialog.propTypes = {
  accountSettingOpen: PropTypes.bool.isRequired,
  setAccountSettingOpen: PropTypes.func.isRequired,
  onSelectYear: PropTypes.func.isRequired,
  userMe: PropTypes.object.isRequired,
};
