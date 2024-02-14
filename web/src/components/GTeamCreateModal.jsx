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

import { getUser } from "../slices/user";
import { createGTeam } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function GTeamCreateModal(props) {
  const { open, setOpen, closeTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [gteamName, setGTeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");

  useEffect(() => {
    closeTeamSelector();
    setGTeamName(null);
    setContactInfo("");
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const handleCreate = async () => {
    const data = {
      gteam_name: gteamName,
      contact_info: contactInfo,
    };
    await createGTeam(data)
      .then(async (response) => {
        enqueueSnackbar("create gteam succeeded", { variant: "success" });
        setOpen(false);
        // fix user.gteams before navigating, to avoid overwriting gteamId by pages/App.jsx.
        await dispatch(getUser());
        const newParams = new URLSearchParams();
        newParams.set("gteamId", response.data.gteam_id);
        navigate("/gteam?" + newParams.toString());
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" },
        );
      });
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography variant="h5">Create GTeam</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => setOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column">
            <TextField
              label="GTeam name"
              onChange={(event) => setGTeamName(event.target.value)}
              required
              error={!gteamName}
              margin="dense"
            ></TextField>
            <TextField
              label="Contact Info"
              onChange={(event) => setContactInfo(event.target.value)}
              margin="dense"
            ></TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreate} disabled={!gteamName} sx={modalCommonButtonStyle}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

GTeamCreateModal.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
  closeTeamSelector: PropTypes.func.isRequired,
};
