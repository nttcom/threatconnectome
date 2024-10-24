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
import { useDeleteATeamMemberMutation } from "../services/tcApi";
import { getATeamAuth, getATeamMembers } from "../slices/ateam";
import { errorToString } from "../utils/func";

export function ATeamMemberRemoveModal(props) {
  const { userId, userName, ateamId, ateamName, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();
  const [deleteATeamMember] = useDeleteATeamMemberMutation();

  const dispatch = useDispatch();

  const handleRemove = async () => {
    function onSuccess(success) {
      console.log("aaa");
      dispatch(getATeamAuth(ateamId));
      dispatch(getATeamMembers(ateamId));
      enqueueSnackbar(`Remove ${userName} from ${ateamName} succeeded`, { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(`Remove member failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    await deleteATeamMember({ ateamId, userId })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <DialogTitle>
        <Box display="flex" flexDirection="row">
          <Typography className={dialogStyle.dialog_title}>Confirm</Typography>
          <Box flexGrow={1} />
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexWrap="wrap" alignItems="baseline">
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
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Button onClick={handleRemove} className={dialogStyle.delete_btn}>
          Remove
        </Button>
      </DialogActions>
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
