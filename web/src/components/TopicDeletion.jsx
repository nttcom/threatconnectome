import { Button, Box, Modal, Typography } from "@mui/material";
import { red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getPTeamTagsSummary, unget } from "../slices/pteam";
import { deleteTopic } from "../utils/api";
import { commonButtonStyle, modalCommonButtonStyle, sxModal } from "../utils/const";

export default function TopicDeletion(props) {
  const { topicId, setOpenTopicModal, onDelete } = props;
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
          dispatch(getPTeamTagsSummary(pteamId)),
          dispatch(unget("topicsSummary")),
          onDelete && onDelete(),
          enqueueSnackbar("delete topic succeeded", { variant: "success" }),
        ]);
      })
      .catch((error) => operationError(error));
    setOpenTopicModal(false);
  }

  const style = {
    ...sxModal,
    maxWidth: "80%",
  };

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
      <Modal hideBackdrop open={open} onClose={() => setOpen(false)}>
        <>
          <Box sx={{ ...style }}>
            <Typography variant="h5">Confirm</Typography>
            <Typography>Are you sure you want to delete this topic?</Typography>
            <Typography>This deletion affects other pteams.</Typography>

            <Box display="flex">
              <Box flexGrow={1} />
              <Button onClick={() => setOpen(false)} sx={{ ...modalCommonButtonStyle, mt: 1 }}>
                Cancel
              </Button>
              <Button
                onClick={handleDelete}
                sx={{
                  ...modalCommonButtonStyle,
                  color: red[700],
                  ml: 1,
                  mt: 1,
                }}
              >
                Delete
              </Button>
            </Box>
          </Box>
        </>
      </Modal>
    </>
  );
}

TopicDeletion.propTypes = {
  topicId: PropTypes.string.isRequired,
  setOpenTopicModal: PropTypes.func.isRequired,
  onDelete: PropTypes.func,
};
