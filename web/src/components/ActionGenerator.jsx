import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  TextField,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import dialogStyle from "../cssModule/dialog.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetTagsQuery } from "../services/tcApi";
import { actionTypes } from "../utils/const";
import { errorToString } from "../utils/func";

export function ActionGenerator(props) {
  const { text, tagIds, action, onGenerate, onEdit, onCancel } = props;

  if (Boolean(onGenerate) === Boolean(onEdit)) {
    throw new Error("Internal Error: Ambiguous mode");
  }

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skip });

  const [actionType, setActionType] = useState(action?.action_type ?? null);
  const [actionTemplate, setActionTemplate] = useState(null);

  const [productName, setProductName] = useState(null);
  const [productVersion, setProductVersion] = useState(null);
  const [description, setDescription] = useState(action?.action ?? null);
  const [actionTagIds, setActionTagIds] = useState([]);

  useEffect(() => {
    if (allTags) {
      setActionTagIds(
        allTags.filter((tag) => action?.ext?.tags?.includes(tag.tag_name)).map((tag) => tag.tag_id),
      );
    }
  }, [allTags, action]);

  const [actionVulnerables, setActionVulnerables] = useState(
    action?.ext?.vulnerable_versions
      ? Object.entries(action.ext.vulnerable_versions).reduce(
          (ret, item) => ({
            ...ret,
            [item[0]]: item[1].join(" || "),
          }),
          {},
        )
      : {},
  );

  if (skip) return <></>;
  if (allTagsError) return <>{`Cannot get allTags: ${errorToString(allTagsError)}`}</>;
  if (allTagsIsLoading) return <>Now loading allTags...</>;

  const cancelButton = onCancel ? (
    <IconButton onClick={() => onCancel()}>
      <CloseIcon />
    </IconButton>
  ) : (
    <></>
  );

  const PF = (name, multiline, onChange) => (
    <TextField
      label={name}
      fullWidth={multiline}
      multiline={multiline}
      required
      size="small"
      sx={{ my: 1, ...(!multiline && { mx: 1 }) }}
      onChange={(event) => onChange(event.target.value)}
    />
  );
  const ProductName = PF("Product Name", false, setProductName);
  const ProductVersion = PF("Product Version", false, setProductVersion);
  const Description = PF("Description", true, setDescription);

  const actionTemplates = {
    Update: {
      UI: (
        <Box alignItems="center" display="flex" flexDirection="row">
          Update {ProductName} to version {ProductVersion}
        </Box>
      ),
      createText: () =>
        productName && productVersion
          ? `Update ${productName} to version ${productVersion}`
          : undefined,
    },
    Patch: {
      UI: (
        <>
          <Box alignItems="center" display="flex" flexDirection="row">
            Patch {ProductName} according to the following instructions:
          </Box>
          <Box display="flex" flexDirection="column" flexGrow={1}>
            {Description}
          </Box>
        </>
      ),
      createText: () =>
        productName && description
          ? `Patch ${productName} according to the following instructions: ${description}`
          : undefined,
    },
    "Adopt Delylist": {
      UI: (
        <>
          <Box alignItems="center" display="flex" flexDirection="row">
            Adopt the following settings to the Denylist of security appliance:
          </Box>
          <Box display="flex" flexDirection="column" flexGrow={1}>
            {Description}
          </Box>
        </>
      ),
      createText: () =>
        description
          ? `Adopt the following settings to the Denylist of security appliance: ${description}`
          : undefined,
    },
    "Stop Service": {
      UI: (
        <Box alignItems="center" display="flex" flexDirection="row">
          Stop the service using {ProductName}
        </Box>
      ),
      createText: () => (productName ? `Stop the service using ${productName}.` : undefined),
    },
    Other: {
      UI: (
        <Box display="flex" flexDirection="column" flexGrow={1}>
          {Description}
        </Box>
      ),
      createText: () => (description ? `${description}` : undefined),
    },
  };

  const createExt = () => {
    const extTags = allTags.filter((tag) => actionTagIds.includes(tag.tag_id));
    return {
      tags: extTags.map((tag) => tag.tag_name),
      vulnerable_versions: extTags
        .map((tag) => tag.tag_name)
        .reduce(
          // omit if not in tags or empty
          (ret, val) => ({
            ...ret,
            ...(actionVulnerables?.[val]?.trim().length > 0
              ? { [val]: [actionVulnerables[val].trim()] }
              : {}),
          }),
          {},
        ),
    };
  };

  const buttonDisabled = () => {
    if (onGenerate) {
      if (!actionType) return true;
      const createText = actionTemplates?.[actionTemplate]?.["createText"];
      if (!createText) return true;
      const actionText = createText();
      if (!actionText) return true;
      return false;
    }
    return false; // FIXME
  };

  const tagsEditor = tagIds ? (
    <List>
      {allTags
        .filter((tag) => tagIds.includes(tag.tag_id))
        .map((tag) => {
          const tagName = tag.tag_name;
          const checked = actionTagIds.includes(tag.tag_id);
          const onClick = checked
            ? () => setActionTagIds(actionTagIds.filter((item) => item !== tag.tag_id))
            : () => setActionTagIds([...actionTagIds, tag.tag_id]);
          return (
            <ListItem key={tag.tag_id} disablePadding divider>
              <ListItemButton
                edge="start"
                onClick={onClick}
                alignItems="center"
                disableGutters
                sx={{ width: 40, flexGrow: 0, flexShrink: 0 }}
              >
                <ListItemIcon>
                  <Checkbox checked={checked} />
                </ListItemIcon>
              </ListItemButton>
              <Box display="flex" flexDirection="column">
                <ListItemText
                  primary={tagName}
                  primaryTypographyProps={{
                    style: {
                      whiteSpace: "nowrap",
                      overflow: "auto",
                      textOverflow: "ellipsis",
                    },
                  }}
                  sx={{ mt: 1, mb: 0, width: 512 }}
                />
                <TextField
                  placeholder={"vulnerable versions: describe with <,<=,>,>=,= and ||"}
                  variant="standard"
                  fullWidth
                  value={actionVulnerables[tagName]}
                  onChange={(event) =>
                    setActionVulnerables({
                      ...actionVulnerables,
                      [tagName]: event.target.value,
                    })
                  }
                  sx={{ overlow: "hidden" }}
                />
              </Box>
            </ListItem>
          );
        })}
    </List>
  ) : (
    <></>
  );

  const actionDescriptionEditor = onEdit ? (
    <>
      <TextField
        label="Action Type"
        required
        select
        size="small"
        sx={{ mr: 1, my: 1, width: 200 }}
        value={actionType ?? ""}
        onChange={(event) => setActionType(event.target.value)}
      >
        {actionTypes.map((type) => (
          <MenuItem key={type} value={type}>
            {type}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label="Description"
        required
        size="small"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
    </>
  ) : (
    <>
      <Box display="flex" flexDirection="row" alignItems="center">
        <TextField
          label="Action Type"
          required
          select
          size="small"
          sx={{ mr: 1, my: 1, width: 200 }}
          value={actionType ?? ""}
          onChange={(event) => setActionType(event.target.value)}
        >
          {actionTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Action Template"
          required
          select
          size="small"
          sx={{ my: 1, width: 300 }}
          value={actionTemplate ?? ""}
          onChange={(event) => {
            setActionTemplate(event.target.value);
          }}
        >
          {Object.keys(actionTemplates).map((key) => (
            <MenuItem key={key} value={key}>
              {key}
            </MenuItem>
          ))}
        </TextField>
      </Box>
      <Box display="flex" flexDirection="column" flexGrow={1} sx={{ overflowY: "auto" }}>
        {actionTemplates?.[actionTemplate]?.["UI"]}
      </Box>
    </>
  );

  return (
    <>
      <Box display="flex" flexDirection="column" flexGrow={1}>
        <Box display="flex" flexDirection="row">
          <Typography className={dialogStyle.dialog_title}>
            {onEdit ? "Edit action" : "Create action"}
          </Typography>
          <Box flexGrow={1} />
          {cancelButton}
        </Box>
        {actionDescriptionEditor}
        <Typography sx={{ mt: 2 }}>
          {"Select artifact tags to which this action should be applied."}
        </Typography>
        {tagsEditor}
        <Box display="flex" flexDirection="row" sx={{ mt: 1 }}>
          <Box flexGrow={1} />
          <Button
            disabled={buttonDisabled()}
            onClick={() => {
              if (onGenerate) {
                onGenerate({
                  action_id: null,
                  action_type: actionType,
                  action: actionTemplates[actionTemplate]["createText"](),
                  ext: createExt(),
                  recommended: false,
                });
              } else {
                onEdit({
                  action_id: action.action_id,
                  action_type: actionType,
                  action: description,
                  ext: createExt(),
                  recommended: action.recommended,
                });
              }
            }}
            className={dialogStyle.submit_btn}
          >
            {text}
          </Button>
        </Box>
      </Box>
    </>
  );
}

ActionGenerator.propTypes = {
  text: PropTypes.string.isRequired,
  tagIds: PropTypes.array.isRequired,
  action: PropTypes.shape({
    action_id: PropTypes.string,
    action: PropTypes.string,
    action_type: PropTypes.string,
    recommended: PropTypes.bool,
    ext: PropTypes.shape({
      tags: PropTypes.array,
      vulnerable_versions: PropTypes.object,
    }),
  }),
  onGenerate: PropTypes.func,
  onEdit: PropTypes.func,
  onCancel: PropTypes.func,
};
