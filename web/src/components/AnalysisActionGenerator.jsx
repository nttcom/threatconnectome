import {
  Delete as DeleteIcon,
  FiberManualRecord as FiberManualRecordIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  Divider,
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
import { grey, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import { actionTypes, modalCommonButtonStyle } from "../utils/const";
import { collectZonesRelatedTeams, errorToString } from "../utils/func";

import { ZoneSelectorModal } from "./ZoneSelectorModal";

export function AnalysisActionGenerator(props) {
  const { text, tagIds, action, myZones, onGenerate, onEdit, onCancel } = props;

  if (Boolean(onGenerate) === Boolean(onEdit)) {
    throw new Error("Internal Error: Ambiguous mode");
  }

  const allTags = useSelector((state) => state.tags.allTags);

  const { enqueueSnackbar } = useSnackbar();

  const [actionType, setActionType] = useState(action?.action_type ?? null);
  const [actionTemplate, setActionTemplate] = useState(null);

  const [productName, setProductName] = useState(null);
  const [productVersion, setProductVersion] = useState(null);
  const [description, setDescription] = useState(action?.action ?? null);
  const [actionTagIds, setActionTagIds] = useState(
    allTags.filter((tag) => action?.ext?.tags?.includes(tag.tag_name)).map((tag) => tag.tag_id)
  );
  const [actionVulnerables, setActionVulnerables] = useState(
    action?.ext?.vulnerable_versions
      ? Object.entries(action.ext.vulnerable_versions).reduce(
          (ret, item) => ({
            ...ret,
            [item[0]]: item[1].join(" || "),
          }),
          {}
        )
      : {}
  );
  const defaultZoneNames =
    action?.zones?.length > 0
      ? typeof action.zones[0] === "string"
        ? action.zones
        : action.zones.map((zone) => zone.zone_name)
      : [];
  const [zoneNames, setZoneNames] = useState(defaultZoneNames);
  const [zonesRelatedTeams, setZonesRelatedTeams] = useState(
    collectZonesRelatedTeams(defaultZoneNames)
  );

  const tryCollectZonesRelatedTeams = async (newZoneNames) => {
    try {
      return await collectZonesRelatedTeams(newZoneNames);
    } catch (error) {
      enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });
    }
  };

  const cancelButton = onCancel ? (
    <Button onClick={onCancel} sx={{ ...modalCommonButtonStyle }}>
      Cancel
    </Button>
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
          {}
        ),
    };
  };

  const buttonDisabled = () => {
    if (onGenerate) {
      const createText = actionTemplates?.[actionTemplate]?.["createText"];
      return (
        !actionType ||
        !createText ||
        !createText() ||
        (zoneNames.length > 0 &&
          Object.values(zonesRelatedTeams?.pteams ?? []).length === 0 &&
          zonesRelatedTeams?.unvisibleExists !== true) // given zones include no teams
      );
    }
    return false;
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
        <Typography variant="h6">{onEdit ? "Edit action" : "Create action"}</Typography>
        {actionDescriptionEditor}
        <Typography sx={{ mt: 2 }}>
          {"Select artifact tags to which this action should be applied."}
        </Typography>
        {tagsEditor}
        <Box display="flex" flexDirection="column" mt={2}>
          <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              Zone
            </Typography>
            <ZoneSelectorModal
              currentZoneNames={zoneNames}
              onApply={async (newZoneNames) => {
                if (newZoneNames.sort().toString() === zoneNames.toString()) return;
                setZonesRelatedTeams(await tryCollectZonesRelatedTeams(newZoneNames));
                setZoneNames(newZoneNames.sort());
              }}
            />
          </Box>
          <List sx={{ ml: 1 }}>
            {zoneNames.map((zoneName) =>
              myZones?.apply?.map((zone) => zone.zone_name).includes(zoneName) ? (
                <Box key={zoneName}>
                  <ListItem
                    disablePadding
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={async () => {
                          const newZoneNames = zoneNames.filter((name) => name !== zoneName);
                          setZonesRelatedTeams(await tryCollectZonesRelatedTeams(newZoneNames));
                          setZoneNames(newZoneNames);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemText
                      primary={zoneName}
                      primaryTypographyProps={{
                        style: {
                          whiteSpace: "nowrap",
                          overflow: "auto",
                          textOverflow: "ellipsis",
                        },
                      }}
                    />
                  </ListItem>
                  <Divider />
                </Box>
              ) : (
                <Box key={zoneName}>
                  <ListItem disablePadding>
                    <ListItemText
                      primary={zoneName}
                      primaryTypographyProps={{
                        style: {
                          color: "grey",
                          whiteSpace: "nowrap",
                          overflow: "auto",
                          textOverflow: "ellipsis",
                        },
                      }}
                    />
                  </ListItem>
                  <Divider />
                </Box>
              )
            )}
          </List>
        </Box>
        <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            PTeams which this action reaches
          </Typography>
        </Box>
        <List sx={{ ml: 1 }}>
          {zoneNames.length === 0 ? (
            <>All of PTeams</>
          ) : zonesRelatedTeams?.pteams === undefined ? (
            <Typography sx={{ color: "red" }}>Something went wrong</Typography>
          ) : Object.values(zonesRelatedTeams.pteams).length > 0 ||
            zonesRelatedTeams.unvisibleExists === true ? (
            <>
              {Object.values(zonesRelatedTeams.pteams).map((pteam) => (
                <ListItem key={pteam.pteam_id} disablePadding>
                  <FiberManualRecordIcon sx={{ m: 1, color: grey[500], fontSize: "small" }} />
                  <ListItemText
                    primary={pteam.pteam_name}
                    primaryTypographyProps={{
                      style: {
                        whiteSpace: "nowrap",
                        overflow: "auto",
                        textOverflow: "ellipsis",
                      },
                    }}
                  />
                </ListItem>
              ))}
              {zonesRelatedTeams.unvisibleExists && (
                <ListItem disablePadding>
                  <FiberManualRecordIcon sx={{ m: 1, color: red[500], fontSize: "small" }} />
                  <ListItemText
                    primary={"(some teams you cannot access to)"}
                    primaryTypographyProps={{
                      style: {
                        color: "orange",
                        whiteSpace: "nowrap",
                        overflow: "auto",
                        textOverflow: "ellipsis",
                      },
                    }}
                  />
                </ListItem>
              )}
            </>
          ) : (
            <Typography sx={{ color: "red" }}>No PTeams</Typography>
          )}
        </List>
        <Box display="flex" flexDirection="row" sx={{ mt: 1 }}>
          <Box flexGrow={1} />
          {cancelButton}
          <Button
            disabled={buttonDisabled()}
            onClick={() => {
              if (onGenerate) {
                onGenerate({
                  action_id: null,
                  action_type: actionType,
                  action: actionTemplates[actionTemplate]["createText"](),
                  ext: createExt(),
                  zones: zoneNames,
                  recommended: false,
                });
              } else {
                onEdit({
                  action_id: action.action_id,
                  action_type: actionType,
                  action: description,
                  ext: createExt(),
                  zones: zoneNames,
                  recommended: action.recommended,
                });
              }
            }}
            sx={{ ...modalCommonButtonStyle, ml: 1 }}
          >
            {text}
          </Button>
        </Box>
      </Box>
    </>
  );
}

AnalysisActionGenerator.propTypes = {
  text: PropTypes.string.isRequired,
  tagIds: PropTypes.array.isRequired,
  action: PropTypes.shape({
    action_id: PropTypes.string,
    action: PropTypes.string,
    action_type: PropTypes.string,
    recommended: PropTypes.bool,
    zones: PropTypes.arrayOf(
      PropTypes.shape({
        zone_name: PropTypes.string,
      })
    ),
    ext: PropTypes.shape({
      tags: PropTypes.array,
      vulnerable_versions: PropTypes.object,
    }),
  }),
  myZones: PropTypes.array.isRequired,
  onGenerate: PropTypes.func,
  onEdit: PropTypes.func,
  onCancel: PropTypes.func,
};
