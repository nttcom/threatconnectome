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

import dialogStyle from "../../cssModule/dialog.module.css";
import { useDeleteTopicMutation } from "../../services/tcApi";
import { commonButtonStyle } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function TopicDeleteModal(props) {
  const { topicId, onSetOpenTopicModal, onDelete } = props;
  const [open, setOpen] = useState(false);
  const [deleteTopic] = useDeleteTopicMutation();

  const { enqueueSnackbar } = useSnackbar();

  function handleDelete() {
    deleteTopic(topicId)
      .unwrap()
      .then(async () => {
        await Promise.all([
          onDelete && onDelete(),
          enqueueSnackbar("delete topic succeeded", { variant: "success" }),
        ]);
      })
      .catch(
        (error) =>
          enqueueSnackbar(`Operation failed: ${errorToString(error)}`, {
            variant: "error",
          }),
        onSetOpenTopicModal(false),
      );
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
};
