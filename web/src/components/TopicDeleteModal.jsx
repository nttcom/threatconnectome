import { Close as CloseIcon } from "@mui/icons-material";
import {
  Button,
  Box,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from "@mui/material";
import { red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import dialogStyle from "../cssModule/dialog.module.css";
import { getPTeamServiceTagsSummary } from "../slices/pteam";
import { deleteTopic } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export function TopicDeleteModal(props) {
  const { topicId, onSetOpenTopicModal, onDelete, serviceId } = props;
  const [open, setOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const dispatch = useDispatch();

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  function handleDelete() {
    deleteTopic(topicId)
      .then(async () => {
        await Promise.all([
          dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId })),
          onDelete && onDelete(),
          enqueueSnackbar("delete topic succeeded", { variant: "success" }),
        ]);
      })
      .catch((error) => operationError(error));
    onSetOpenTopicModal(false);
  }

  return (
    <>
      <Button
        onClick={() => setOpen(true)}
        sx={{
          ...commonButtonStyle,
          bgcolor: red[700],
          "&:hover": {
            bgcolor: red[900],
          },
          mr: 1,
        }}
      >
        Delete Topic
      </Button>
      <Dialog hideBackdrop open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              Confirm
            </Typography>
            <IconButton onClick={() => setOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this topic?</Typography>
          <Typography>This deletion affects other pteams.</Typography>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Box>
            <Box sx={{ flex: "1 1 auto" }} />
            <Button onClick={handleDelete} className={dialogStyle.delete_btn}>
              Delete
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
}

TopicDeleteModal.propTypes = {
  topicId: PropTypes.string.isRequired,
  onSetOpenTopicModal: PropTypes.func.isRequired,
  onDelete: PropTypes.func,
  serviceId: PropTypes.string.isRequired,
};
