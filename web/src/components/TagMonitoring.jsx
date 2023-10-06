import {
  Add as AddIcon,
  ChatBubbleOutline as ChatBubbleOutlineIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Typography,
  Grid,
  ListItem,
  ListItemText,
  IconButton,
  TextField,
  Tooltip,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { FixedSizeList } from "react-window";

import { getPTeamTagsSummary } from "../slices/pteam";
import { getTags } from "../slices/tags";
import { createTag, addPTeamTag, removePTeamTag } from "../utils/api";

export default function TagMonitoring(props) {
  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const pteamTags = useSelector((state) => state.pteam.tagsSummary.tags); // dispatched by App
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const [searchAllTags, setSearchAllTags] = useState("");
  const [createTagMode, setCreateTagMode] = useState(false);
  const [filteredAllTags, setFilteredAllTags] = useState([]);
  const [pteamTagIds, setPTeamTagIds] = useState(new Set());
  const [sortedPTeamTags, setSortedPTeamTags] = useState([]);
  const [searchPTeamTags, setSearchPTeamTags] = useState("");
  const [filteredPTeamTags, setFilteredPTeamTags] = useState([]);

  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    if (allTags) {
      setFilteredAllTags(
        allTags.filter((tag) => fixedTag(tag.tag_name).match(fixedTag(searchAllTags)))
      );
    }
  }, [allTags, searchAllTags]);

  useEffect(() => {
    if (pteamTags) {
      setPTeamTagIds(new Set(pteamTags.map((t) => t.tag_id)));
      setSortedPTeamTags([...pteamTags].sort((a, b) => a.tag_name.localeCompare(b.tag_name)));
    }
  }, [pteamTags]);

  useEffect(() => {
    if (sortedPTeamTags) {
      setFilteredPTeamTags(
        sortedPTeamTags.filter((tag) => fixedTag(tag.tag_name).match(fixedTag(searchPTeamTags)))
      );
    }
  }, [sortedPTeamTags, searchPTeamTags]);

  const fixedTag = (orig) => orig.trim().toLowerCase(); // normalize to compare

  const operationError = (error) => {
    const resp = error.response;
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const handleCreateTag = async (tagName) => {
    if (tagName === "") return;
    await createTag({ tag_name: tagName })
      .then(() => {
        dispatch(getTags());
        setCreateTagMode(false);
        enqueueSnackbar("add new tag succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleAddToMonitorList = async (addTag) => {
    await addPTeamTag(pteamId, addTag.tag_id, {})
      .then(() => {
        dispatch(getPTeamTagsSummary(pteamId));
        enqueueSnackbar("add to monitoring list succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleRemoveFromMonitorList = async (removeTag) => {
    await removePTeamTag(pteamId, removeTag.tag_id)
      .then(() => {
        dispatch(getPTeamTagsSummary(pteamId));
        enqueueSnackbar("remove from monitoring list succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const allTagRow = ({ index, style }) => (
    <>
      {index !== filteredAllTags.length ? (
        <ListItem key={filteredAllTags[index].tag_id} style={style}>
          <ListItemText
            primary={filteredAllTags[index].tag_name}
            primaryTypographyProps={{
              style: {
                whiteSpace: "nowrap",
                overflow: "auto",
                textOverflow: "ellipsis",
              },
            }}
          />
          {!pteamTagIds.has(filteredAllTags[index].tag_id) && (
            <IconButton edge="end" onClick={() => handleAddToMonitorList(filteredAllTags[index])}>
              <AddIcon />
            </IconButton>
          )}
        </ListItem>
      ) : (
        <ListItem style={style}>
          {!createTagMode ? (
            <Button onClick={() => setCreateTagMode(true)} sx={{ textTransform: "none" }}>
              + Add new tag
            </Button>
          ) : (
            <Box>
              <TextField
                size="small"
                label="Target name"
                onKeyDown={(e) => {
                  e.key === "Enter" && handleCreateTag(e.target.value);
                }}
              ></TextField>
              <Button onClick={() => setCreateTagMode(false)} sx={{ textTransform: "none" }}>
                Cancel
              </Button>
            </Box>
          )}
        </ListItem>
      )}
    </>
  );

  const pteamTagRow = ({ index, style }) => (
    <ListItem key={filteredPTeamTags[index].tag_id} style={style}>
      <ListItemText
        primary={filteredPTeamTags[index].tag_name}
        primaryTypographyProps={{
          style: {
            whiteSpace: "nowrap",
            overflow: "auto",
            textOverflow: "ellipsis",
          },
        }}
      />
      {filteredPTeamTags[index].text && (
        <Tooltip title={filteredPTeamTags[index].text}>
          <ChatBubbleOutlineIcon edge="end" />
        </Tooltip>
      )}
      <IconButton edge="end" onClick={() => handleRemoveFromMonitorList(filteredPTeamTags[index])}>
        <DeleteIcon />
      </IconButton>
    </ListItem>
  );

  return (
    <Box display="flex" flexDirection="column">
      <Box>
        <Typography sx={{ fontWeight: 900 }}>All tags</Typography>
        <Box alignItems="flex-end" display="flex" mb={1}>
          <SearchIcon />
          <TextField
            label="Search for all tags"
            variant="standard"
            onChange={(event) => setSearchAllTags(event.target.value)}
          />
        </Box>
        <Grid border={`solid ${grey[300]}`}>
          <FixedSizeList
            height={190}
            width="100%"
            itemCount={filteredAllTags.length + 1} // Append "Add new tag" row
            itemSize={35}
          >
            {allTagRow}
          </FixedSizeList>
        </Grid>
      </Box>
      <Box mt={3}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Current monitoring list
        </Typography>
        <Box alignItems="flex-end" display="flex" mb={1}>
          <SearchIcon />
          <TextField
            label="Search for monitoring tags"
            variant="standard"
            onChange={(event) => setSearchPTeamTags(event.target.value)}
          />
        </Box>
        <Grid border={`solid ${grey[300]}`}>
          <FixedSizeList
            height={190}
            width="100%"
            itemCount={filteredPTeamTags.length}
            itemSize={35}
          >
            {pteamTagRow}
          </FixedSizeList>
        </Grid>
      </Box>
    </Box>
  );
}
