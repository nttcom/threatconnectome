import CloseIcon from "@mui/icons-material/Close";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { Box, IconButton, MenuItem, Select, Stack, Tooltip, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { DeleteAccountDialog } from "../DeleteAccountDialog";

import { ChangeEmailDialog } from "./ChangeEmailDialog";
import { UpdatePasswordDialog } from "./UpdatePasswordDialog";
import { CHANGE_EMAIL_DIALOG_STATES, UPDATE_PASSWORD_DIALOG_STATES } from "./dialogStates";

export function AccountSettingsDialog(props) {
  const { accountSettingOpen, setAccountSettingOpen, onSelectYear, userMe } = props;

  const handleClose = () => {
    setAccountSettingOpen(false);
  };

  // Change Email is not implemented
  const changeEmaildisabled = true;
  // Change Password is not implemented
  const changePasswordDisabled = true;

  const [changeEmailOpen, setChangeEmailOpen] = useState(CHANGE_EMAIL_DIALOG_STATES.NONE);
  const [updatePasswordOpen, setUpdatePasswordOpen] = useState(UPDATE_PASSWORD_DIALOG_STATES.NONE);

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
                onClick={() => {
                  setChangeEmailOpen(CHANGE_EMAIL_DIALOG_STATES.SEND_VERIFICATION_EMAIL);
                }}
              >
                Change Email
              </Button>
              <ChangeEmailDialog open={changeEmailOpen} setOpen={setChangeEmailOpen} />
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
              <Button
                variant="contained"
                size="small"
                disabled={changePasswordDisabled}
                onClick={() => {
                  setUpdatePasswordOpen(UPDATE_PASSWORD_DIALOG_STATES.UPDATE_PASSWORD);
                }}
              >
                Change Password
              </Button>
              <UpdatePasswordDialog open={updatePasswordOpen} setOpen={setUpdatePasswordOpen} />
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                Team
              </Typography>
              <Stack spacing={1}>
                {userMe.pteam_roles.map((pteam_role) => (
                  <DialogContentText key={pteam_role.pteam.pteam_name}>
                    {pteam_role.pteam.pteam_name}
                  </DialogContentText>
                ))}
              </Stack>
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
