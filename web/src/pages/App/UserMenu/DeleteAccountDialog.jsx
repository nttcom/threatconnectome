import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { Box, Stack, TextField, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import { useState } from "react";

export function DeleteAccountDialog(props) {
  const { userMe } = props;

  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleDeleteAccount = () => {
    // Delete my account is not implemented
    if (email !== userMe.email) {
      return;
    }
    handleClose();
  };

  // Delete my account is not implemented
  const deleteAccountDisabled = true;

  return (
    <>
      <Button
        color="error"
        onClick={handleClickOpen}
        sx={{ p: 0 }}
        disabled={deleteAccountDisabled}
      >
        Delete my account
      </Button>
      <Dialog open={open} onClose={handleClose} maxWidth="xs">
        <Box sx={{ pt: 2, display: "flex", justifyContent: "center" }}>
          <ErrorOutlineIcon fontSize="large" color="error" />
        </Box>
        <DialogTitle sx={{ textAlign: "center" }}>Delete your account permanantly?</DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <DialogContentText>
              This action cannot be undone. This will permanentlly delete your account.
            </DialogContentText>
            <Box>
              <Typography>Type in your email to confirm</Typography>
              <TextField
                hiddenLabel
                variant="filled"
                size="small"
                onChange={(event) => setEmail(event.target.value)}
                sx={{ width: 1 }}
                error={false}
                placeholder="sample@example.com"
                // helperText="The email you entered was incorrect."
              ></TextField>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center" }}>
          <Stack spacing={1}>
            <Button variant="contained" color="error" onClick={handleDeleteAccount}>
              Permanently delete account
            </Button>
            <Button sx={{ color: "grey" }} onClick={handleClose}>
              Cancel
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>
    </>
  );
}
DeleteAccountDialog.propTypes = {
  userMe: PropTypes.object.isRequired,
};
