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

import dialogStyle from "../cssModule/dialog.module.css";
import { useRemoveWatchingPTeamMutation } from "../services/tcApi";
import { errorToString } from "../utils/func";

export function ATeamWatchingStop(props) {
  const { watchingPteamId, watchingPteamName, ateamId, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();
  const [removeWatchingPTeam] = useRemoveWatchingPTeamMutation();

  const handleRemove = async () => {
    function onSuccess(success) {
      enqueueSnackbar(`Stop watching ${watchingPteamName} succeeded`, {
        variant: "success",
      });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Stop watching target failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    await removeWatchingPTeam({ ateamId: ateamId, pteamId: watchingPteamId })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            Confirm
          </Typography>
          {onClose && (
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      </DialogTitle>
      <DialogContent>
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
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Box display="flex">
          <Box flexGrow={1} />
          <Button onClick={handleRemove} className={dialogStyle.delete_btn}>
            Stop
          </Button>
        </Box>
      </DialogActions>
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
