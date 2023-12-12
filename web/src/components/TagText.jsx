import { Edit as EditIcon, Save as SaveIcon, Undo as UndoIcon } from "@mui/icons-material";
import { Typography, Box, IconButton, TextField } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getPTeamTag, getPTeamTagsSummary } from "../slices/pteam";
import { updatePTeamTag } from "../utils/api";

export function TagText(props) {
  const { pteamId, tagId } = props;

  const [editMode, setEditMode] = useState(false);
  const [currentText, setCurrentText] = useState("");
  const [editingText, setEditingText] = useState("");

  const { enqueueSnackbar } = useSnackbar();

  const pteamtags = useSelector((state) => state.pteam.pteamtags); // dispatched by parent

  const dispatch = useDispatch();

  useEffect(() => {
    if (!pteamtags[tagId]) return;
    setCurrentText(pteamtags[tagId].text);
  }, [pteamtags, tagId]);

  const handleEditMode = () => {
    setEditingText(currentText); // reset textfield value
    setEditMode(!editMode);
  };

  const handleApply = async () => {
    await updatePTeamTag(pteamId, tagId, { text: editingText })
      .then(() => {
        dispatch(getPTeamTag({ pteamId: pteamId, tagId: tagId }));
        dispatch(getPTeamTagsSummary(pteamId));
        setEditMode(false);
        enqueueSnackbar("update tag text succeeded", { variant: "success" });
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      });
  };

  return (
    <Box sx={{ backgroundColor: grey[100] }} p={1}>
      <Box display="flex" justifyContent="space-between" ml={1}>
        <Typography variant="h6">About</Typography>
        <Box>
          <IconButton onClick={() => handleEditMode()}>
            {editMode ? <UndoIcon /> : <EditIcon />}
          </IconButton>
          {editMode && (
            <IconButton onClick={() => handleApply()}>
              <SaveIcon />
            </IconButton>
          )}
        </Box>
      </Box>
      {editMode ? (
        <Box ml={1}>
          <TextField
            fullWidth
            multiline
            defaultValue={editingText}
            onChange={(newValue) => setEditingText(newValue.target.value)}
          />
        </Box>
      ) : (
        <Box sx={{ wordBreak: "break-all", ml: 1 }}>
          {currentText ? currentText : "No description"}
        </Box>
      )}
    </Box>
  );
}

TagText.propTypes = {
  pteamId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
};
