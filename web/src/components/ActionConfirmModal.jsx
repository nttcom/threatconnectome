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
  TextField,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import {
  getPTeamSolvedTaggedTopicIds,
  getPTeamTagsSummary,
  getPTeamTopicStatus,
  getPTeamUnsolvedTaggedTopicIds,
} from "../slices/pteam";
import { createActionLog, createTopicStatus } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

import ActionTypeChip from "./ActionTypeChip";
import RecommendedStar from "./RecommendedStar";
import UUIDTypography from "./UUIDTypography";

export default function ActionConfirmModal(props) {
  const { handleConfirm, selectedActions, setShow, show, topicId } = props;

  const [note, setNote] = useState("");

  const { tagId } = useParams();
  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const topics = useSelector((state) => state.topics); // dispatched by parent
  const user = useSelector((state) => state.user.user);

  const dispatch = useDispatch();

  const handleAction = async () => {
    try {
      const actionLogs = await Promise.all(
        selectedActions.map(
          async (actionId) =>
            await createActionLog({
              action_id: actionId,
              pteam_id: pteamId,
              topic_id: topicId,
              user_id: user.user_id,
            }).then((response) => {
              enqueueSnackbar("Action succeeded", { variant: "success" });
              return response.data;
            })
        )
      );
      await createTopicStatus(pteamId, topicId, tagId, {
        topic_status: "completed",
        logging_ids: actionLogs.map((log) => log.logging_id),
        note: note.trim() || null,
      });
      handleClose();
      handleConfirm();
      setNote("");
      dispatch(getPTeamTagsSummary(pteamId));
      dispatch(getPTeamTopicStatus({ pteamId: pteamId, topicId: topicId, tagId: tagId }));
      dispatch(getPTeamSolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
      dispatch(getPTeamUnsolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
      enqueueSnackbar("Set topicstatus 'completed' succeeded", { variant: "success" });
    } catch (error) {
      enqueueSnackbar(`Operation failed: ${error}`, { variant: "error" });
    }
  };

  if (!pteamId || !topicId || !topics[topicId]) return <></>;

  const handleClose = () => setShow(false);

  return (
    <Dialog fullWidth onClose={handleClose} open={show}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit">
            Confirm the Action
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <Divider />
      <DialogContent>
        <Typography>
          Solve the topic using
          {selectedActions.length === 1 ? " this action" : " these actions"}:
        </Typography>
        {topics[topicId]?.actions &&
          topics[topicId].actions
            .filter((action) => selectedActions.includes(action.action_id))
            .map((action) => (
              <Box
                alignItems="center"
                display="flex"
                flexDirection="row"
                key={action.action_id}
                mb={1}
              >
                <ActionTypeChip actionType={action.action_type} />
                <RecommendedStar disabled={!action.recommended} />
                <Box display="flex" flexDirection="column">
                  <Typography>{action.action}</Typography>
                  <UUIDTypography>{action.action_id}</UUIDTypography>
                </Box>
              </Box>
            ))}
        <TextField
          fullWidth
          label="Evidence (Optional)"
          multiline
          onChange={(event) => setNote(event.target.value)}
          placeholder={
            "Evidence that you have completed the action, such as a report URL, " +
            "event logs, file hashes, etc."
          }
          variant="outlined"
          value={note}
        />
      </DialogContent>
      <DialogActions>
        <Button color="primary" onClick={handleClose} sx={modalCommonButtonStyle}>
          Cancel
        </Button>
        <Button color="primary" onClick={handleAction} sx={modalCommonButtonStyle}>
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
}

ActionConfirmModal.propTypes = {
  handleConfirm: PropTypes.func.isRequired,
  selectedActions: PropTypes.arrayOf(PropTypes.string).isRequired,
  setShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  topicId: PropTypes.string.isRequired,
};
