import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import dialogStyle from "../cssModule/dialog.module.css";
import { useCreateATeamMutation } from "../services/tcApi";
import { getUser } from "../slices/user";
import { errorToString } from "../utils/func";

export function ATeamCreateModal(props) {
  const { open, onOpen, onCloseTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [createATeam] = useCreateATeamMutation();

  const [ateamName, setATeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");

  useEffect(() => {
    onCloseTeamSelector();
    setATeamName(null);
    setContactInfo("");
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const handleCreate = async () => {
    const data = {
      ateam_name: ateamName,
      contact_info: contactInfo,
    };
    await createATeam(data)
      .unwrap()
      .then(async (data) => {
        enqueueSnackbar("create ateam succeeded", { variant: "success" });
        onOpen(false);
        // fix user.ateams before navigating, to avoid overwriting ateamId by pages/App.jsx.
        await dispatch(getUser());
        const newParams = new URLSearchParams();
        newParams.set("ateamId", data.ateam_id);
        navigate("/ateam?" + newParams.toString());
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={() => onOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography className={dialogStyle.dialog_title}>Create ATeam</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => onOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column">
            <TextField
              label="ATeam name"
              onChange={(event) => setATeamName(event.target.value)}
              required
              error={!ateamName}
              margin="dense"
            ></TextField>
            <TextField
              label="Contact Info"
              onChange={(event) => setContactInfo(event.target.value)}
              margin="dense"
            ></TextField>
          </Box>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Button onClick={handleCreate} disabled={!ateamName} className={dialogStyle.submit_btn}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

ATeamCreateModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onOpen: PropTypes.func.isRequired,
  onCloseTeamSelector: PropTypes.func.isRequired,
};
