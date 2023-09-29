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
import { createATeam } from "../utils/api";

export default function ATeamCreationModal(props) {
  const { open, setOpen, closeTeamSelector } = props;
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [ateamName, setATeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");

  useEffect(() => {
    closeTeamSelector();
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
        setOpen(false);
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
      <Dialog fullWidth open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography variant="h5">Create ATeam</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => setOpen(false)}>
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
            <Button
              onClick={handleCreate}
              color="success"
              variant="contained"
              disabled={!ateamName}
            >
              Create
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </>
  );
}

ATeamCreationModal.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
  closeTeamSelector: PropTypes.func.isRequired,
};
