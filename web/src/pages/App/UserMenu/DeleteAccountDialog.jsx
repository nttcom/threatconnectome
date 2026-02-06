import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { Box, Stack, TextField, Typography } from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useDispatch } from "react-redux";

import { useAuth } from "../../../hooks/auth";
import { tcApi, useDeleteUserMutation } from "../../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../../slices/auth";
import { errorToString } from "../../../utils/func";

export function DeleteAccountDialog(props) {
  const { userMe } = props;
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.DeleteAccountDialog" });

  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const { signOut } = useAuth();

  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");

  const [deleteUser] = useDeleteUserMutation();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleDeleteAccount = async () => {
    if (email === userMe.email) {
      await deleteUser()
        .unwrap()
        .then(async () => {
          dispatch(tcApi.util.resetApiState()); // reset RTKQ
          dispatch(setAuthUserIsReady(false));
          dispatch(setRedirectedFrom({}));
          await signOut();
        })
        .catch((error) => {
          enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), {
            variant: "error",
          });
        });
    } else if (email !== userMe.email) {
      enqueueSnackbar(t("emailWrong"), { variant: "error" });
    }
  };

  return (
    <>
      <Button color="error" onClick={handleClickOpen} sx={{ p: 0 }}>
        {t("deleteButton")}
      </Button>
      <Dialog open={open} onClose={handleClose} maxWidth="xs">
        <Box sx={{ pt: 2, display: "flex", justifyContent: "center" }}>
          <ErrorOutlineIcon fontSize="large" color="error" />
        </Box>
        <DialogTitle sx={{ textAlign: "center" }}>{t("title")}</DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <DialogContentText>{t("warning")}</DialogContentText>
            <Box>
              <Typography>{t("confirmPrompt")}</Typography>
              <TextField
                hiddenLabel
                variant="filled"
                size="small"
                onChange={(event) => setEmail(event.target.value)}
                sx={{ width: 1 }}
                error={false}
                placeholder={t("placeholder")}
                // helperText="The email you entered was incorrect."
              ></TextField>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center" }}>
          <Stack spacing={1}>
            <Button variant="contained" color="error" onClick={handleDeleteAccount}>
              {t("deleteConfirm")}
            </Button>
            <Button sx={{ color: "grey" }} onClick={handleClose}>
              {t("cancel")}
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
