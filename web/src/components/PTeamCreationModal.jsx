import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { getUser } from "../slices/user";
import { createPTeam } from "../utils/api";

export default function PTeamCreationModal(props) {
  const { open, setOpen, closeTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [pteamName, setPTeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");
  const [slackUrl, setSlackUrl] = useState("");

  useEffect(() => {
    closeTeamSelector();
    setPTeamName(null);
    setContactInfo("");
    setSlackUrl("");
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const handleCreate = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
      slack_webhook_url: slackUrl,
    };
    await createPTeam(data)
      .then(async (response) => {
        enqueueSnackbar("create pteam succeeded", { variant: "success" });
        setOpen(false);
        // fix user.pteams before navigating, to avoid overwriting pteamId by pages/App.jsx.
        await dispatch(getUser());
        const newParams = new URLSearchParams();
        newParams.set("pteamId", response.data.pteam_id);
        navigate("/pteam?" + newParams.toString());
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      });
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography variant="h5">Create PTeam</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => setOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column">
            <TextField
              label="PTeam name"
              onChange={(event) => setPTeamName(event.target.value)}
              required
              error={!pteamName}
              margin="dense"
            ></TextField>
            <TextField
              label="Contact Info"
              onChange={(event) => setContactInfo(event.target.value)}
              margin="dense"
            ></TextField>
            <TextField
              label="Slack's Incoming Webhook URL"
              onChange={(event) => setSlackUrl(event.target.value)}
              margin="dense"
            ></TextField>
            <Button
              onClick={handleCreate}
              color="success"
              variant="contained"
              disabled={!pteamName}
            >
              Create
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </>
  );
}

PTeamCreationModal.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
  closeTeamSelector: PropTypes.func.isRequired,
};
