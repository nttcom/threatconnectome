import {
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
import { green, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import { TabPanel } from "../components/TabPanel";
import dialogStyle from "../cssModule/dialog.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useCreateActionMutation,
  useDeleteActionMutation,
  useGetUserMeQuery,
  useUpdateActionMutation,
  useUpdateTopicMutation,
} from "../services/tcApi";
import { a11yProps, errorToString, setEquals, validateNotEmpty } from "../utils/func";

import { ActionTypeIcon } from "./ActionTypeIcon";
import { AnalysisActionGeneratorModal } from "./AnalysisActionGeneratorModal";
import { ThreatImpactChip } from "./ThreatImpactChip";
import { TopicTagSelectorModal } from "./TopicTagSelectorModal";

export function TopicEditModalChild(props) {
  const { open, onSetOpen, currentTopic, currentActions, allTags } = props;

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

  const skip = useSkipUntilAuthTokenIsReady();

  const { enqueueSnackbar } = useSnackbar();
  const [createAction] = useCreateActionMutation();
  const [updateAction] = useUpdateActionMutation();
  const [deleteAction] = useDeleteActionMutation();

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  const createActionTagOptions = (tagIdList) => {
    return allTags
      .filter((tag) => tagIdList.includes(tag.tag_id) || tagIdList.includes(tag.parent_id))
      .map((tag) => tag.tag_id);
  };

  const resetParams = () => {
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

  useEffect(() => {
    if (!open) return;
    if (topicId === currentTopic.topic_id) return;
    resetParams();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const handleClose = () => {
    resetParams();
    onSetOpen(false);
  };

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
            .then(() => enqueueSnackbar("Updating topic succeeded", { variant: "success" }));
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
                <TopicTagSelectorModal
                  tagIds={tagIds}
                  setTagIds={setTagIds}
                  setActionTagOptions={setActionTagOptions}
                  createActionTagOptions={createActionTagOptions}
                />
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
          </Box>
        </TabPanel>
        <TabPanel index={2} value={tab}>
          <Box display="flex" flexDirection="column" mt={2}>
            <Box display="flex" flexDirection="row" alignItems="center" mb={1}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Action
              </Typography>
              <AnalysisActionGeneratorModal
                actionTagOptions={actionTagOptions}
                actions={actions}
                setActions={setActions}
              />
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

TopicEditModalChild.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  currentTopic: PropTypes.object.isRequired,
  currentActions: PropTypes.array.isRequired,
  allTags: PropTypes.array.isRequired,
};
