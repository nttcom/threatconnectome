import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { WaitingModal } from "../components/WaitingModal";
import {
  getPTeamSolvedTaggedTopicIds,
  getPTeamUnsolvedTaggedTopicIds,
  getPTeamTagsSummary,
} from "../slices/pteam";
import { autoCloseTag } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export function PTeamTagAutoClose(props) {
  const { tagId } = props;
  const [isOpenWaitingModal, setIsOpenWaitingModal] = useState(false);
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);

  const handleSave = async () => {
    setIsOpenWaitingModal(true);
    await autoCloseTag(pteamId, tagId)
      .then(() => {
        enqueueSnackbar("Auto Close Accepted", { variant: "success" });
        dispatch(getPTeamSolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
        dispatch(getPTeamUnsolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
        dispatch(getPTeamTagsSummary(pteamId));
        // TODO: topic.status is changed when a autocolse button is pressed.
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      })
      .finally(() => {
        setIsOpenWaitingModal(false);
      });
  };

  return (
    <Box>
      <Box display="flex" flexDirection="row" alignItems="center">
        <Typography variant="body2" mb={1} mr={2}>
          Manually check alerts that require a response.
        </Typography>
        <Button onClick={handleSave} sx={{ ...commonButtonStyle, mb: 1 }}>
          Run
        </Button>
      </Box>
      <WaitingModal isOpen={isOpenWaitingModal} text="Trying auto close" />
    </Box>
  );
}

PTeamTagAutoClose.propTypes = {
  tagId: PropTypes.string.isRequired,
};
