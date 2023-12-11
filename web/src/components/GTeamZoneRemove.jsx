import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getGTeamZonesSummary } from "../slices/gteam";
import { deleteGTeamZone } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function GTeamZoneRemove(props) {
  const { gteamId, zoneName, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getGTeamZonesSummary(gteamId));
      enqueueSnackbar("Remove zone succeeded", { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove zone failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await deleteGTeamZone(gteamId, zoneName)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h5">Confirm</Typography>
      <Box display="flex" alignItems="baseline" sx={{ my: 2 }}>
        <Typography>Are you sure you want to remove zone: {zoneName}?</Typography>
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

GTeamZoneRemove.propTypes = {
  gteamId: PropTypes.string.isRequired,
  zoneName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
