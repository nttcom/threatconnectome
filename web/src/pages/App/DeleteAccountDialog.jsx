import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { Box, Stack, TextField, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import React, { useState } from "react";

export function DeleteAccountDialog() {
  const [open, setOpen] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  return (
    <>
      <Button color="error" onClick={handleClickOpen} sx={{ p: 0 }}>
        Delete my account
      </Button>
      <Dialog open={open} onClose={handleClose} maxWidth="xs">
        <Box sx={{ pt: 2, display: "flex", justifyContent: "center" }}>
          <ErrorOutlineIcon fontSize="large" color="error" />
        </Box>
        <DialogTitle sx={{ textAlign: "center" }}>
          Delete your entire account permanantly?
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <DialogContentText>
              This action cannot be undone. This will permanentlly delete your entire account.
            </DialogContentText>
            <Box>
              <Typography>Type in your password to confirm</Typography>
              <TextField
                hiddenLabel
                variant="filled"
                size="small"
                sx={{ width: 1 }}
                error={false}
                // helperText="The password you entered was incorrect."
              ></TextField>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center" }}>
          <Stack spacing={1}>
            <Button variant="contained" color="error" onClick={handleClose}>
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
