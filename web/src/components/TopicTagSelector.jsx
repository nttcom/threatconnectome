import { Search as SearchIcon, Upload as UploadIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { FixedSizeList } from "react-window";

import { getTags } from "../slices/tags";
import { createTag } from "../utils/api";
import { modalCommonButtonStyle, commonButtonStyle } from "../utils/const";

export default function TopicTagSelector(props) {
  const { currentSelectedIds, onCancel, onApply, sx } = props;

  const [filteredTags, setFilteredTags] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedIds, setSelectedIds] = useState(currentSelectedIds);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const fixedTag = (orig) => orig.trim().toLowerCase(); // normalize to compare

  useEffect(() => {
    if (allTags) {
      setFilteredTags(allTags.filter((tag) => fixedTag(tag.tag_name).match(fixedTag(search))));
    }
  }, [allTags, search]);

  const handleCreateTag = async () => {
    function onSuccess(success) {
      dispatch(getTags());
      enqueueSnackbar("Create tag succeeded", { variant: "success" });
      setSearch("");
    }
    function onError(error) {
      enqueueSnackbar(`Create tag failed: ${error.response?.data?.detail}`, { variant: "error" });
    }
    await createTag({ tag_name: search.trim() })
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  if (!allTags) return <></>;

  const createDisabled =
    !fixedTag(search) ||
    filteredTags.filter((tmp) => fixedTag(tmp.tag_name) === fixedTag(search)).length > 0;
  const tagRow = ({ index, style }) => {
    const targetId = filteredTags[index].tag_id;
    const targetName = filteredTags[index].tag_name;
    const checked = selectedIds.includes(targetId);
    const onClick = !onApply
      ? undefined
      : checked
      ? () => setSelectedIds(selectedIds.filter((tmp) => tmp !== targetId))
      : () => setSelectedIds([...selectedIds, targetId]);
    return (
      <ListItem key={index} style={style} disablePadding>
        <ListItemButton edge="start" onClick={onClick} disableGutters sx={{ py: 0 }}>
          <ListItemIcon>
            <Checkbox checked={checked} />
          </ListItemIcon>
          <ListItemText
            primary={targetName}
            primaryTypographyProps={{
              style: {
                whiteSpace: "nowrap",
                overflow: "auto",
                textOverflow: "ellipsis",
              },
            }}
          />
        </ListItemButton>
      </ListItem>
    );
  };

  return (
    <Box sx={{ ...sx, display: "flex" }}>
      <Box display="flex" flexDirection="column">
        <Typography fontWeight={900} mb={2}>
          Select tags
        </Typography>
        <Box display="flex" flexDirection="row" alignItems="center">
          <Box display="flex" flexGrow={1} />
          <SearchIcon sx={{ ml: 2 }} />
          <TextField
            label="Search / Create "
            variant="outlined"
            value={search}
            size="small"
            onChange={(event) => setSearch(event.target.value)}
          />
          <Button
            disabled={createDisabled}
            onClick={handleCreateTag}
            sx={{ ...commonButtonStyle, ml: 1, mr: 1 }}
          >
            <UploadIcon />
            Create new tag
          </Button>
        </Box>
        <Box
          display="flex"
          flexDirection="column"
          flexGrow={1}
          alignItems="left"
          sx={{ overflowY: "auto", border: 1, m: 1, p: 1 }}
        >
          <FixedSizeList height={400} itemSize={35} itemCount={filteredTags.length}>
            {tagRow}
          </FixedSizeList>
        </Box>
        {(onApply || onCancel) && (
          <Box display="flex" flexDirection="row">
            <Box flexGrow={1} />
            {onCancel && (
              <Button onClick={() => onCancel()} sx={{ ...modalCommonButtonStyle, mr: 1 }}>
                Cancel
              </Button>
            )}
            {onApply && (
              <Button
                onClick={() => {
                  onApply(selectedIds);
                }}
                sx={{ ...modalCommonButtonStyle, mr: 1 }}
              >
                Apply
              </Button>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}

TopicTagSelector.propTypes = {
  currentSelectedIds: PropTypes.array.isRequired,
  onCancel: PropTypes.func,
  onApply: PropTypes.func,
  sx: PropTypes.object,
};
