import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getWatchingPTeams } from "../slices/ateam";
import { removeWatchingPTeam } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export default function ATeamWatchingStop(props) {
  const { watchingPteamId, watchingPteamName, ateamId, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getWatchingPTeams(ateamId));
      enqueueSnackbar(`Stop watching ${watchingPteamName} succeeded`, {
        variant: "success",
      });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Stop watching target failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await removeWatchingPTeam(ateamId, watchingPteamId)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h5">Confirm</Typography>
      <Box display="flex" alignItems="baseline" sx={{ my: 2 }}>
        <Typography>Are you sure you want to stop watching </Typography>
        <Typography
          variant="h6"
          noWrap
          sx={{ fontWeight: "bold", textDecoration: "underline", mx: 1 }}
        >
          {watchingPteamName}
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
          Stop
        </Button>
      </Box>
    </>
  );
}

ATeamWatchingStop.propTypes = {
  watchingPteamId: PropTypes.string.isRequired,
  watchingPteamName: PropTypes.string.isRequired,
  ateamId: PropTypes.string.isRequired,
  ateamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
