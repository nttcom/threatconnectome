import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  TextField,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export function ChangeEmailDialog(props) {
  const { open, setOpen } = props;
  return (
    <>
      <Dialog open={open === 1} maxWidth="xs" fullWidth>
        <Box sx={{ position: "relative" }}>
          <DialogTitle sx={{ textAlign: "center" }}>Verify email address</DialogTitle>
          <IconButton
            sx={{ position: "absolute", right: 8, top: 8 }}
            onClick={() => setOpen(false)}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <DialogContent>
          <DialogContentText>
            {"Your current email address is "}
            <strong>sample@example.com</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpen(2)}>
            Send Verification Code
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={open === 2} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
        <Box sx={{ position: "relative" }}>
          <DialogTitle sx={{ textAlign: "center" }}>Enter code</DialogTitle>
          <IconButton
            sx={{ position: "absolute", right: 8, top: 8 }}
            onClick={() => setOpen(false)}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <DialogContent>
          <DialogContentText>
            {"Your current email address is "}
            <strong>sample@example.com</strong>.{" "}
            {"We'll need to verify your old email address in order to change it."}
          </DialogContentText>
          <TextField
            hiddenLabel
            size="small"
            sx={{ width: 1, mt: 2 }}
            placeholder="Enter Verification code"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpen(3)}>
            Continue
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={open === 3} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
        <Box sx={{ position: "relative" }}>
          <DialogTitle sx={{ textAlign: "center" }}>Change your email address</DialogTitle>
          <IconButton
            sx={{ position: "absolute", right: 8, top: 8 }}
            onClick={() => setOpen(false)}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <DialogContent>
          <DialogContentText>
            Enter a new email address and your existing password.
          </DialogContentText>
          <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="New email address" />
          <TextField hiddenLabel size="small" sx={{ width: 1, mt: 2 }} label="Current password" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              /* Add email change logic here */
              setOpen(false);
            }}
          >
            Change email
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

ChangeEmailDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
};
