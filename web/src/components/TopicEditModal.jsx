import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
  FiberManualRecord as FiberManualRecordIcon,
  SentimentSatisfiedAlt as SentimentSatisfiedAltIcon,
  SentimentVeryDissatisfied as SentimentVeryDissatisfiedIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Tab,
  Tabs,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { blue, grey, green, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import TabPanel from "../components/TabPanel";
import { getActions, getTopic } from "../slices/topics";
import { getAuthorizedZones } from "../slices/user";
import { createAction, deleteAction, updateAction, updateTopic } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";
import {
  a11yProps,
  collectZonesRelatedTeams,
  errorToString,
  setEquals,
  validateNotEmpty,
} from "../utils/func";

import ActionTypeIcon from "./ActionTypeIcon";
import { AnalysisActionGenerator } from "./AnalysisActionGenerator";
import ThreatImpactChip from "./ThreatImpactChip";
import TopicTagSelector from "./TopicTagSelector";
import { ZoneSelectorModal } from "./ZoneSelectorModal";

export function TopicEditModal(props) {
  const { open, setOpen, currentTopic, currentActions } = props;

  const [topicId, setTopicId] = useState("");
  const [title, setTitle] = useState("");
  const [threatImpact, setThreatImpact] = useState(1);
  const [abst, setAbst] = useState("");
  const [actions, setActions] = useState([]);
  const [zoneNames, setZoneNames] = useState([]);
  const [zonesRelatedTeams, setZonesRelatedTeams] = useState(undefined);
  const [actionTagOptions, setActionTagOptions] = useState([]);

  const [tagIds, setTagIds] = useState([]);
  const [tab, setTab] = useState(0);
  const [updating, setUpdating] = useState(false);

  const allTags = useSelector((state) => state.tags.allTags);
  const myZones = useSelector((state) => state.user.zones);
  const userMe = useSelector((state) => state.user.user);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  useEffect(() => {
    if (myZones === undefined) dispatch(getAuthorizedZones());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!open) return;
    if (topicId === currentTopic.topic_id) return;
    resetParams();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const createActionTagOptions = (tagIdList) => {
    if (!allTags) return [];
    return allTags
      .filter((tag) => tagIdList.includes(tag.tag_id) || tagIdList.includes(tag.parent_id))
      .map((tag) => tag.tag_id);
  };

  const resetParams = async () => {
    // reset with currentTopic
    setTab(0);
    setTopicId(currentTopic.topic_id);
    setTitle(currentTopic.title);
    setThreatImpact(currentTopic.threat_impact);
    setAbst(currentTopic.abstract);
    const newTagIds = currentTopic.tags.map((tag) => tag.tag_id);
    setTagIds(newTagIds);
    setActionTagOptions(createActionTagOptions(newTagIds));
    setActions(currentActions);
    setZoneNames(currentTopic.zones.map((zone) => zone.zone_name));
    setZonesRelatedTeams(
      await tryCollectZonesRelatedTeams(currentTopic.zones.map((zone) => zone.zone_name))
    );
  };

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const tryCollectZonesRelatedTeams = async (newZoneNames) => {
    try {
      return await collectZonesRelatedTeams(newZoneNames);
    } catch (error) {
      operationError(error);
    }
  };

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const handleClose = () => setOpen(false);

  const handleUpdate = async () => {
    setUpdating(true);
    try {
      const topicData = {
        title: title === currentTopic.title ? null : title,
        abstract: abst === currentTopic.abstract ? null : abst,
        threat_impact: threatImpact === currentTopic.threat_impact ? null : threatImpact,
        tags: setEquals(new Set(tagIds), new Set(currentTopic.tags.map((tag) => tag.tag_id)))
          ? null
          : allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
        zone_names: setEquals(
          new Set(zoneNames),
          new Set(currentTopic.zones.map((zone) => zone.zone_name))
        )
          ? null
          : zoneNames,
      };
      if (Object.values(topicData).filter((item) => item !== null).length > 0) {
        // something modified
        if (currentTopic.created_by === userMe.user_id) {
          enqueueSnackbar("Updating topic.", { variant: "info" });
          await updateTopic(topicId, topicData).then(async (response) => {
            await Promise.all([
              enqueueSnackbar("Updating topic succeeded", { variant: "success" }),
              dispatch(getTopic(topicId)),
            ]);
          });
        } else {
          enqueueSnackbar("Skip updating topic params (Not a topic creator)", {
            variant: "warning",
          });
        }
      }
      // fix actions
      let newActions = [];
      let updatedActions = [];
      let keptActionIds = [];
      for (const action of actions) {
        if (action.action_id === null) {
          newActions.push(action);
        } else {
          keptActionIds.push(action.action_id);
          const orig = currentActions.find((item) => item.action_id === action.action_id);
          if (orig?.recommended !== action.recommended) {
            updatedActions.push(action);
          }
        }
      }
      const removedActionIds = currentActions
        .map((action) => action.action_id)
        .filter((actionId) => !keptActionIds.includes(actionId));
      if (newActions.length > 0) {
        enqueueSnackbar("Adding actions", { variant: "info" });
        for (const action of newActions) {
          await createAction({ ...action, topic_id: currentTopic.topic_id });
        }
        enqueueSnackbar("Adding actions succeeded", { variant: "success" });
      }
      if (updatedActions.length > 0) {
        enqueueSnackbar("Updating actions", { variant: "info" });
        for (const action of updatedActions) {
          await updateAction(action.action_id, { recommended: action.recommended });
        }
        enqueueSnackbar("Updating actions succeeded", { variant: "success" });
      }
      if (removedActionIds.length > 0) {
        enqueueSnackbar("Removing actions", { variant: "info" });
        for (const actionId of removedActionIds) {
          await deleteAction(actionId);
        }
        enqueueSnackbar("Remofing actions succeeded", { variant: "success" });
      }
      if (newActions.length + updatedActions.length + removedActionIds.length > 0) {
        await dispatch(getActions(currentTopic.topic_id));
      }
      setTopicId(""); // mark reset at next open, only if succeeded
    } catch (error) {
      enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });
      // Note: params are kept on failed values
    } finally {
      setUpdating(false);
      setOpen(false);
    }
  };

  const readyForUpdate = () =>
    !updating &&
    validateNotEmpty(title) &&
    (title !== currentTopic.title ||
      threatImpact !== currentTopic.threat_impact ||
      abst !== currentTopic.abstract ||
      !setEquals(new Set(tagIds), new Set(currentTopic.tags.map((tag) => tag.tag_id))) ||
      !setEquals(new Set(zoneNames), new Set(currentTopic.zones.map((zone) => zone.zone_name))) ||
      JSON.stringify(actions) !== JSON.stringify(currentActions)) &&
    !(
      zoneNames.length > 0 &&
      Object.values(zonesRelatedTeams?.pteams ?? []).length === 0 &&
      zonesRelatedTeams?.unvisibleExists !== true
    );

  function TopicTagSelectorModal() {
    const [tagOpen, setTagOpen] = useState(false);
    return (
      <>
        <IconButton onClick={() => setTagOpen(true)} sx={{ color: blue[700] }}>
          <AddBoxIcon />
        </IconButton>
        <Dialog open={tagOpen} onClose={() => setTagOpen(false)}>
          <DialogContent>
            <TopicTagSelector
              currentSelectedIds={tagIds}
              onCancel={() => setTagOpen(false)}
              onApply={(newTagIds) => {
                setTagIds(newTagIds);
                setActionTagOptions(createActionTagOptions(newTagIds));
                setTagOpen(false);
              }}
            />
          </DialogContent>
        </Dialog>
      </>
    );
  }

  function AnalysisActionGeneratorModal() {
    const [generatorOpen, setGeneratorOpen] = useState(false);
    return (
      <>
        <IconButton onClick={() => setGeneratorOpen(true)} sx={{ color: blue[700] }}>
          <AddBoxIcon />
        </IconButton>
        <Dialog open={generatorOpen} onClose={() => setGeneratorOpen(false)}>
          <DialogContent>
            <AnalysisActionGenerator
              text="Add action"
              tagIds={actionTagOptions}
              myZones={myZones ?? []}
              onGenerate={(ret) => {
                setActions([...actions, ret]);
                setGeneratorOpen(false);
              }}
              onCancel={() => setGeneratorOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </>
    );
  }

  if (!allTags || !myZones) return <>Now loading...</>;

  return (
    <Dialog open={open === true} maxWidth="md" fullWidth sx={{ maxHeight: "100vh" }}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
            Edit Topic
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box borderBottom={1} borderBottomColor="divider">
          <Tabs aria-label="tabs" onChange={handleChangeTab} value={tab}>
            <Tab label="Content" {...a11yProps(0)} />
            <Tab label="Dissemination" {...a11yProps(1)} />
            <Tab label="Response planning" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel index={0} value={tab}>
          <Box display="flex" flexDirection="column" sx={{ m: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mt: 2 }}>
              Title
            </Typography>
            <TextField
              size="small"
              required
              variant="outlined"
              value={title}
              error={!validateNotEmpty(title)}
              onChange={(event) => setTitle(event.target.value)}
              mb={4}
              sx={{ minWidth: "400px" }}
            />
            <Typography variant="body2" sx={{ fontWeight: 600, mt: 2 }}>
              Topic ID(UUID)
            </Typography>
            <Typography>{topicId}</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, mt: 2 }}>
              Threat impact
            </Typography>
            <ButtonGroup variant="outlined">
              {[1, 2, 3, 4].map((impact) => (
                <Button key={impact} variant="text" onClick={() => setThreatImpact(impact)}>
                  <ThreatImpactChip
                    threatImpact={impact}
                    reverse={parseInt(threatImpact) !== impact}
                    sx={{ cursor: "pointer" }}
                  />
                </Button>
              ))}
            </ButtonGroup>
            <Typography variant="body2" sx={{ fontWeight: 600, mt: 2 }}>
              Abstract
            </Typography>
            <Box sx={{ display: "flex" }}>
              <TextField
                value={abst}
                onChange={(event) => {
                  setAbst(event.target.value);
                }}
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                sx={{ minWidth: "480px" }}
              />
              {abst === "" ? (
                <SentimentVeryDissatisfiedIcon sx={{ color: red[600], mt: 9, ml: 1 }} />
              ) : (
                <SentimentSatisfiedAltIcon sx={{ color: green[600], mt: 9, ml: 1 }} />
              )}
            </Box>
          </Box>
        </TabPanel>
        <TabPanel index={1} value={tab}>
          <Box display="flex" flexDirection="column" sx={{ m: 2 }}>
            <Box display="flex" flexDirection="column" mt={2}>
              <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Artifact Tag
                </Typography>
                <TopicTagSelectorModal />
              </Box>
              <List sx={{ ml: 1 }}>
                {allTags
                  .filter((tag) => tagIds.includes(tag.tag_id))
                  .map((tag) => (
                    <Box key={tag.tag_name}>
                      <ListItem
                        key={tag.tag_name}
                        disablePadding
                        secondaryAction={
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => {
                              const newTagIds = tagIds.filter((tagId) => tagId !== tag.tag_id);
                              setTagIds(newTagIds);
                              setActionTagOptions(createActionTagOptions(newTagIds));
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        }
                      >
                        <ListItemText
                          primary={tag.tag_name}
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
                  ))}
              </List>
            </Box>
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
                {zoneNames.map((zoneName, index) =>
                  myZones?.apply?.map((zone) => zone.zone_name).includes(zoneName) ? (
                    <Box key={index}>
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
                    <Box key={index}>
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
                The PTeam that the topic reaches
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
          </Box>
        </TabPanel>
        <TabPanel index={2} value={tab}>
          <Box display="flex" flexDirection="column" mt={2}>
            <Box display="flex" flexDirection="row" alignItems="center" mb={1}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Action
              </Typography>
              <AnalysisActionGeneratorModal />
            </Box>
            <List sx={{ ml: 1 }}>
              {actions.map((action) => (
                <Box key={action.action}>
                  <ListItem
                    key={action.action}
                    disablePadding
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => setActions(actions.filter((item) => item !== action))}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <IconButton
                      onClick={() =>
                        setActions(
                          actions.map((item) =>
                            item !== action ? item : { ...action, recommended: !action.recommended }
                          )
                        )
                      }
                      sx={{ pb: 0.5 }}
                    >
                      <ActionTypeIcon
                        disabled={!action.recommended}
                        actionType={action.action_type}
                      />
                    </IconButton>
                    <ListItemText
                      primary={action.action}
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
              ))}
            </List>
          </Box>
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Box sx={{ display: "flex", flexDirection: "row", mr: 1, mb: 1 }}>
          <Box sx={{ flex: "1 1 auto" }} />
          <Button disabled={!readyForUpdate()} sx={modalCommonButtonStyle} onClick={handleUpdate}>
            Update
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

TopicEditModal.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
  currentTopic: PropTypes.object.isRequired,
  currentActions: PropTypes.array.isRequired,
};
