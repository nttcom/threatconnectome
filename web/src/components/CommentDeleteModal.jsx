import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";

import dialogStyle from "../cssModule/dialog.module.css";
import { useDeleteATeamTopicCommentMutation } from "../services/tcApi";
import { dateTimeFormat } from "../utils/func";

export function CommentDeleteModal(props) {
  const { comment, onClose } = props;

  const { enqueueSnackbar } = useSnackbar();
  const [apiDeleteATeamTopicComment] = useDeleteATeamTopicCommentMutation();

  const handleAction = async () => {
    await apiDeleteATeamTopicComment(comment.ateam_id, comment.topic_id, comment.comment_id)
      .unwrap()
      .then(() => onClose())
      .catch((error) => {
        enqueueSnackbar(
          "Operation failed: " +
            `${error.response.status} ${error.response.statusText} ${error.response.data?.detail}`,
          { variant: "error" },
        );
      });
  };

  return (
    <Dialog open={Boolean(comment?.comment_id)} onClose={onClose} fullWidth>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            Confirm
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body">Are you sure you want to delete comment below?</Typography>
        <Divider sx={{ my: 2 }} />
        <Box display="flex" alignItems="center" mb={1}>
          <Typography variant="subtitle2" fontWeight="900" mr={2}>
            {comment?.email}
          </Typography>
          <Typography variant="subtitle2">{dateTimeFormat(comment?.created_at)}</Typography>
          {comment?.updated_at && (
            <Typography variant="subtitle2" sx={{ ml: 1 }}>
              {`(updated at ${dateTimeFormat(comment?.updated_at)})`}
            </Typography>
          )}
        </Box>
        <Box mb={1} sx={{ backgroundColor: grey[100], padding: "10px" }}>
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {comment?.comment}
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Button onClick={handleAction} className={dialogStyle.delete_btn}>
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
}
CommentDeleteModal.propTypes = {
  comment: PropTypes.object,
  onClose: PropTypes.func.isRequired,
};
