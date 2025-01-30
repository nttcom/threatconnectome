import {
  Close as CloseIcon,
  Search as SearchIcon,
  Upload as UploadIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  IconButton,
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
import { FixedSizeList } from "react-window";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useCreateTagMutation, useGetTagsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { commonButtonStyle } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function TopicTagSelector(props) {
  const { currentSelectedIds, onCancel, onApply, sx } = props;

  const [filteredTags, setFilteredTags] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedIds, setSelectedIds] = useState(currentSelectedIds);

  const { enqueueSnackbar } = useSnackbar();

  const [createTag] = useCreateTagMutation();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skip });

  const fixedTag = (orig) => orig.trim().toLowerCase(); // normalize to compare

  useEffect(() => {
    if (allTags) {
      setFilteredTags(allTags.filter((tag) => fixedTag(tag.tag_name).match(fixedTag(search))));
    }
  }, [allTags, search]);

  if (skip) return <></>;
  if (allTagsError) throw new APIError(errorToString(allTagsError), { api: "getTags" });
  if (allTagsIsLoading) return <>Now loading allTags...</>;

  const handleCreateTag = async () => {
    function onSuccess(success) {
      enqueueSnackbar("Create tag succeeded", { variant: "success" });
      setSearch("");
    }
    function onError(error) {
      enqueueSnackbar(`Create tag failed: ${errorToString(error)}`, { variant: "error" });
    }
    await createTag({ tag_name: search.trim() })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

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
        <Box display="flex" flexDirection="row">
          <Typography className={dialogStyle.dialog_title}>Select tags</Typography>
          <Box flexGrow={1} />
          {onCancel && (
            <IconButton onClick={() => onCancel()}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>
        <Box display="flex" flexDirection="row" alignItems="center" sx={{ mt: 1 }}>
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
            {onApply && (
              <Button
                onClick={() => {
                  onApply(selectedIds);
                }}
                className={dialogStyle.submit_btn}
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
