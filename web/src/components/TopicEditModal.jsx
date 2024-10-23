import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
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
  ToggleButtonGroup,
  ToggleButton,
  Stack,
} from "@mui/material";
import { blue, green, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { TabPanel } from "../components/TabPanel";
import dialogStyle from "../cssModule/dialog.module.css";
import {
  useCreateActionMutation,
  useUpdateActionMutation,
  useDeleteActionMutation,
  useUpdateTopicMutation
} from "../services/tcApi";
import { getActions, getTopic } from "../slices/topics";
import { a11yProps, errorToString, setEquals, validateNotEmpty } from "../utils/func";

import { ActionTypeIcon } from "./ActionTypeIcon";
import { AnalysisActionGenerator } from "./AnalysisActionGenerator";
import { ThreatImpactChip } from "./ThreatImpactChip";
import { TopicTagSelector } from "./TopicTagSelector";

export function TopicEditModal(props) {
  const { open, onSetOpen, currentTopic, currentActions } = props;

  const [topicId, setTopicId] = useState("");
  const [title, setTitle] = useState("");
  const [threatImpact, setThreatImpact] = useState(1);
  const [abst, setAbst] = useState("");
  const [actions, setActions] = useState([]);
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [automatable, setAutomatable] = useState(currentTopic.automatable);
  const [exploitation, setExploitation] = useState(currentTopic.exploitation);
  const [tagIds, setTagIds] = useState([]);
  const [tab, setTab] = useState(0);
  const [updating, setUpdating] = useState(false);
  const [updateTopic] = useUpdateTopicMutation();

  const allTags = useSelector((state) => state.tags.allTags);
  const userMe = useSelector((state) => state.user.user);

  const { enqueueSnackbar } = useSnackbar();
  const [createAction] = useCreateActionMutation();
  const [updateAction] = useUpdateActionMutation();
  const [deleteAction] = useDeleteActionMutation();
  const dispatch = useDispatch();

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
    setAutomatable(currentTopic.automatable);
    setExploitation(currentTopic.exploitation);
  };

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const handleClose = () => onSetOpen(false);

  const handleUpdate = async () => {
    setUpdating(true);
    try {
      // update topic if updated
      const topicData = {
        title: title === currentTopic.title ? null : title,
        abstract: abst === currentTopic.abstract ? null : abst,
        threat_impact: threatImpact === currentTopic.threat_impact ? null : threatImpact,
        tags: setEquals(new Set(tagIds), new Set(currentTopic.tags.map((tag) => tag.tag_id)))
          ? null
          : allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
        automatable: automatable === currentTopic.automatable ? null : automatable,
        exploitation: exploitation === currentTopic.exploitation ? null : exploitation,
      };
      if (Object.values(topicData).filter((item) => item !== null).length > 0) {
        // something modified
        if (currentTopic.created_by === userMe.user_id) {
          enqueueSnackbar("Updating topic.", { variant: "info" });
          await updateTopic({ topicId, data: topicData })
            .unwrap()
            .then(async (response) => {
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
      const newActions = actions.filter((action) => action.action_id === null);
      const keptActions = actions.filter((action) => action.action_id !== null);
      const updatedActions = keptActions.filter((action) => {
        const originalAction = currentActions.find((item) => item.action_id === action.action_id);
        return originalAction?.recommended !== action.recommended;
      });
      const keptActionIds = keptActions.map((action) => action.action_id);
      const removedActionIds = currentActions
        .map((action) => action.action_id)
        .filter((actionId) => !keptActionIds.includes(actionId));
      // call api to create,update,remove actions
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
          await updateAction({
            actionId: action.action_id,
            data: { recommended: action.recommended },
          });
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
      onSetOpen(false);
    }
  };

  const readyForUpdate = () =>
    !updating &&
    validateNotEmpty(title) &&
    (title !== currentTopic.title ||
      threatImpact !== currentTopic.threat_impact ||
      abst !== currentTopic.abstract ||
      automatable !== currentTopic.automatable ||
      exploitation !== currentTopic.Exploitation ||
      !setEquals(new Set(tagIds), new Set(currentTopic.tags.map((tag) => tag.tag_id))) ||
      JSON.stringify(actions) !== JSON.stringify(currentActions));

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
          <AnalysisActionGenerator
            text="Add action"
            tagIds={actionTagOptions}
            onGenerate={(ret) => {
              setActions([...actions, ret]);
              setGeneratorOpen(false);
            }}
            onCancel={() => setGeneratorOpen(false)}
          />
        </Dialog>
      </>
    );
  }

  if (!allTags) return <>Now loading...</>;

  return (
    <Dialog open={open === true} maxWidth="md" sx={{ maxHeight: "100vh" }}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            Edit Topic
          </Typography>
          <IconButton onClick={handleClose}>
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
            <Tab label="SSVC" {...a11yProps(3)} />
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
            <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                The PTeam that the topic reaches
              </Typography>
            </Box>
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
                            item === action
                              ? { ...action, recommended: !action.recommended }
                              : item,
                          ),
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
        <TabPanel index={3} value={tab}>
          <Stack spacing={1}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Automatable
              </Typography>
              <ToggleButtonGroup color="primary" value={automatable}>
                <ToggleButton value="no" onClick={() => setAutomatable("no")}>
                  No
                </ToggleButton>
                <ToggleButton value="yes" onClick={() => setAutomatable("yes")}>
                  Yes
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Exploitation
              </Typography>
              <ToggleButtonGroup color="primary" value={exploitation}>
                <ToggleButton value="none" onClick={() => setExploitation("none")}>
                  None
                </ToggleButton>
                <ToggleButton value="public_poc" onClick={() => setExploitation("public_poc")}>
                  Public PoC
                </ToggleButton>
                <ToggleButton value="active" onClick={() => setExploitation("active")}>
                  Active
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Stack>
        </TabPanel>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Box sx={{ display: "flex", flexDirection: "row" }}>
          <Box sx={{ flex: "1 1 auto" }} />
          <Button
            disabled={!readyForUpdate()}
            onClick={handleUpdate}
            className={dialogStyle.submit_btn}
          >
            Update
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

TopicEditModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  currentTopic: PropTypes.object.isRequired,
  currentActions: PropTypes.array.isRequired,
};
