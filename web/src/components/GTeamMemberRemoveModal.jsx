import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getGTeamAuth, getGTeamMembers } from "../slices/gteam";
import { deleteGTeamMember } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function GTeamMemberRemoveModal(props) {
  const { userId, userName, gteamId, gteamName, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getGTeamAuth(gteamId));
      dispatch(getGTeamMembers(gteamId));
      enqueueSnackbar(`Remove ${userName} from ${gteamName} succeeded`, { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove member failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await deleteGTeamMember(gteamId, userId)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h5">Confirm</Typography>
      <Box display="flex" flexWrap="wrap" alignItems="baseline" sx={{ my: 2 }}>
        <Typography>Are you sure you want to remove </Typography>
        <Typography
          variant="h6"
          noWrap
          sx={{ fontWeight: "bold", textDecoration: "underline", mx: 1 }}
        >
          {userName}
        </Typography>
        <Typography>from the gteam </Typography>
        <Typography noWrap sx={{ fontWeight: "bold", ml: 1 }}>
          {gteamName}
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

GTeamMemberRemoveModal.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  gteamId: PropTypes.string.isRequired,
  gteamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
