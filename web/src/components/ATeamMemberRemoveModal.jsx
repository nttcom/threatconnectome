import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getATeamAuth, getATeamMembers } from "../slices/ateam";
import { deleteATeamMember } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function ATeamMemberRemoveModal(props) {
  const { userId, userName, ateamId, ateamName, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      dispatch(getATeamAuth(ateamId));
      dispatch(getATeamMembers(ateamId));
      enqueueSnackbar(`Remove ${userName} from ${ateamName} succeeded`, { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove member failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await deleteATeamMember(ateamId, userId)
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
        <Typography>from the ateam </Typography>
        <Typography noWrap sx={{ fontWeight: "bold", ml: 1 }}>
          {ateamName}
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

ATeamMemberRemoveModal.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  ateamId: PropTypes.string.isRequired,
  ateamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
