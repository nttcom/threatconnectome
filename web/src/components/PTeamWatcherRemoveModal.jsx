import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getPTeamWatcher } from "../slices/pteam";
import { removeWatcherATeam } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function PTeamWatcherRemoveModal(props) {
  const { watcherAteamId, watcherAteamName, pteamId, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getPTeamWatcher(pteamId));
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
      <Typography variant="h5">Confirm</Typography>
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
      <Box display="flex">
        <Box flexGrow={1} />
        {onClose && (
          <Button onClick={onClose} sx={modalCommonButtonStyle}>
            Cancel
          </Button>
        )}
        <Button onClick={handleRemove} sx={{ ...modalCommonButtonStyle, ml: 1 }}>
          Remove
        </Button>
      </Box>
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
