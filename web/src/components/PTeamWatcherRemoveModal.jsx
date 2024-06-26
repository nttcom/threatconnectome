import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import dialogStyle from "../cssModule/dialog.module.css";
import { getPTeam } from "../slices/pteam";
import { removeWatcherATeam } from "../utils/api";

export function PTeamWatcherRemoveModal(props) {
  const { watcherAteamId, watcherAteamName, pteamId, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getPTeam(pteamId));
      enqueueSnackbar(`Remove watcher ${watcherAteamName} succeeded`, {
        variant: "success",
      });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove watcher failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await removeWatcherATeam(pteamId, watcherAteamId)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <DialogTitle>
        <Box display="flex" flexDirection="row">
          <Typography className={dialogStyle.dialog_title}>Confirm</Typography>
          <Box flexGrow={1} />
          {onClose && (
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" alignItems="baseline" sx={{ my: 2 }}>
          <Typography>Are you sure you want to remove watcher </Typography>
          <Typography
            variant="h6"
            noWrap
            sx={{ fontWeight: "bold", textDecoration: "underline", mx: 1 }}
          >
            {watcherAteamName}
          </Typography>
          <Typography>?</Typography>
        </Box>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Button onClick={handleRemove} className={dialogStyle.delete_btn}>
          Remove
        </Button>
      </DialogActions>
    </>
  );
}

PTeamWatcherRemoveModal.propTypes = {
  watcherAteamId: PropTypes.string.isRequired,
  watcherAteamName: PropTypes.string.isRequired,
  pteamId: PropTypes.string.isRequired,
  pteamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
