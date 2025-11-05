import CloseIcon from "@mui/icons-material/Close";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { Box, IconButton, MenuItem, Select, Stack, Tooltip, Typography } from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";

import { DeleteAccountDialog } from "./DeleteAccountDialog";

export function AccountSettingsDialog(props) {
  const { accountSettingOpen, setAccountSettingOpen, onSelectYear, userMe, onSelectDefaultTeam } =
    props;

  const handleClose = () => {
    setAccountSettingOpen(false);
  };

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
            </Box>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                User ID
              </Typography>
              <DialogContentText>{userMe.user_id}</DialogContentText>
            </Box>
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
                defaultValue="none"
                onChange={(e) => {
                  onSelectDefaultTeam(e.target.value);
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
              <DeleteAccountDialog userMe={userMe} />
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
  onSelectDefaultTeam: PropTypes.func.isRequired,
  userMe: PropTypes.object.isRequired,
};
