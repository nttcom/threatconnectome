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
import { getUser } from "../slices/user";
import { createPTeam } from "../utils/api";

export function PTeamCreateModal(props) {
  const { open, onSetOpen, onCloseTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [pteamName, setPTeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");
  const [slackUrl, setSlackUrl] = useState("");

  useEffect(() => {
    onCloseTeamSelector();
    setPTeamName(null);
    setContactInfo("");
    setSlackUrl("");
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const handleCreate = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
      alert_slack: { enable: true, webhook_url: slackUrl },
    };
    await createPTeam(data)
      .then(async (response) => {
        enqueueSnackbar("create pteam succeeded", { variant: "success" });
        onSetOpen(false);
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
          { variant: "error" },
        );
      });
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={() => onSetOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography className={dialogStyle.dialog_title}>Create PTeam</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => onSetOpen(false)}>
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
          </Box>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Button onClick={handleCreate} disabled={!pteamName} className={dialogStyle.submit_btn}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

PTeamCreateModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  onCloseTeamSelector: PropTypes.func.isRequired,
};
