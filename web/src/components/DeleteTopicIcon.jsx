import { Delete as DeleteIcon, Close as CloseIcon } from "@mui/icons-material";
import {
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Tooltip,
  Typography,
} from "@mui/material";
import { grey, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";

import dialogStyle from "../cssModule/dialog.module.css";
import { useDeleteTopicMutation } from "../services/tcApi";
import { commonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

export function DeleteTopicIcon(props) {
  const { topicId, onDelete } = props;

  const [modalOpen, setModalOpen] = useState(false);
  const [deleteTopic] = useDeleteTopicMutation();

  const { enqueueSnackbar } = useSnackbar();

  const handleModalClose = () => {
    setModalOpen(false);
  };

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
        setModalOpen(false),
      );
  }

  return (
    <>
      <Tooltip title="Delete this topic">
        <IconButton onClick={() => setModalOpen(true)}>
          <DeleteIcon />
        </IconButton>
      </Tooltip>
      <Dialog
        open={modalOpen}
        onClose={handleModalClose}
        maxWidth="md"
        fullWidth
        sx={{ maxHeight: "100vh" }}
      >
        <Box
          alignItems="center"
          display="flex"
          flexDirection="row"
          sx={{ backgroundColor: grey[200] }}
        >
          <Typography
            fontWeight="bold"
            flexGrow={1}
            className={dialogStyle.dialog_title}
            sx={{ marginLeft: 2 }}
          >
            DANGER ZONE
          </Typography>
          <IconButton onClick={handleModalClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
        <DialogTitle sx={{ backgroundColor: grey[200] }}>
          <Box
            alignItems="center"
            display="flex"
            flexDirection="row"
            sx={{ bgcolor: "common.white" }}
          >
            <Typography
              fontWeight="bold"
              flexGrow={1}
              className={dialogStyle.dialog_title}
              sx={{ marginLeft: 2 }}
            >
              Delete this topic
            </Typography>
          </Box>
          <Box
            alignItems="center"
            display="flex"
            flexDirection="row"
            sx={{ bgcolor: "common.white" }}
          >
            <Typography flexGrow={1} className={dialogStyle.dialog_title} sx={{ marginLeft: 2 }}>
              Once you delete a topic, there is no going back. Please to certain.
            </Typography>
            <DialogContent sx={{ marginLeft: 10 }}>
              <Button
                onClick={handleDelete}
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
            </DialogContent>
          </Box>
        </DialogTitle>
      </Dialog>
    </>
  );
}
DeleteTopicIcon.propTypes = {
  topicId: PropTypes.string.isRequired,
  onDelete: PropTypes.func,
};
