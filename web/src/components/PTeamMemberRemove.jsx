import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getPTeamAchievements, getPTeamAuth, getPTeamMembers } from "../slices/pteam";
import { deletePTeamMember } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function PTeamMemberRemove(props) {
  const { userId, userName, pteamId, pteamName, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getPTeamAchievements(pteamId));
      dispatch(getPTeamAuth(pteamId));
      dispatch(getPTeamMembers(pteamId));
      enqueueSnackbar(`Remove ${userName} from ${pteamName} succeeded`, { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove member failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await deletePTeamMember(pteamId, userId)
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
        <Typography>from the pteam </Typography>
        <Typography noWrap sx={{ fontWeight: "bold", ml: 1 }}>
          {pteamName}
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

PTeamMemberRemove.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  pteamId: PropTypes.string.isRequired,
  pteamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
