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
import { createATeam } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function ATeamCreateModal(props) {
  const { open, onOpen, onCloseTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

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
      .then(async (response) => {
        enqueueSnackbar("create ateam succeeded", { variant: "success" });
        onOpen(false);
        // fix user.ateams before navigating, to avoid overwriting ateamId by pages/App.jsx.
        await dispatch(getUser());
        const newParams = new URLSearchParams();
        newParams.set("ateamId", response.data.ateam_id);
        navigate("/ateam?" + newParams.toString());
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
      <Dialog fullWidth open={open} onClose={() => onOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography variant="h5">Create ATeam</Typography>
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
        <DialogActions>
          <Button onClick={handleCreate} disabled={!ateamName} sx={modalCommonButtonStyle}>
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
