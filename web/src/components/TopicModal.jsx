import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  ContentPaste as ContentPasteIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Typography,
  List,
} from "@mui/material";
import { blue, grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import uuid from "react-native-uuid";
import { useDispatch, useSelector } from "react-redux";

import dialogStyle from "../cssModule/dialog.module.css";
import {
  getPTeamTopicActions,
  getPTeamServiceTaggedTopicIds,
  getPTeamServiceTagsSummary,
  getPTeamTagsSummary,
} from "../slices/pteam";
import { getTopic } from "../slices/topics";
import {
  createTopic,
  fetchFlashsense,
  updateTopic,
  createAction,
  updateAction,
  deleteAction,
} from "../utils/api";
import { actionTypes } from "../utils/const";
import { validateNotEmpty, validateUUID, arrayComparison } from "../utils/func";

import { ActionGenerator } from "./ActionGenerator";
import { ActionItem } from "./ActionItem";
import { ThreatImpactChip } from "./ThreatImpactChip";
import { TopicDeleteModal } from "./TopicDeleteModal";
import { TopicTagSelector } from "./TopicTagSelector";

const steps = ["Import Flashsense", "Create topic"];

export function TopicModal(props) {
  const {
    open,
    onSetOpen,
    presetTopicId,
    presetTagId,
    presetParentTagId,
    presetActions,
    serviceId,
  } = props;

  const [errors, setErrors] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const [skipped, setSkipped] = useState(new Set());
  const [validErrorMessage, setValidErrorMessage] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const user = useSelector((state) => state.user.user);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const topics = useSelector((state) => state.topics.topics);
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const src = topics[presetTopicId];
  const [topicId, setTopicId] = useState("");
  const [title, setTitle] = useState("");
  const [abst, setAbst] = useState("");
  const [threatImpact, setThreatImpact] = useState(4);
  const [tagIds, setTagIds] = useState([]);
  const [mispTags, setMispTags] = useState("");
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [actions, setActions] = useState([]);
  const [editActionOpen, setEditActionOpen] = useState(false);
  const [editActionTarget, setEditActionTarget] = useState({});

  const dispatch = useDispatch();

  useEffect(() => {
    setErrors([]);
    setActiveStep(presetTopicId ? 1 : 0);
    setSkipped(presetTopicId ? new Set([0]) : new Set());
    setValidErrorMessage(null);
    setTopicId(presetTopicId ?? "");
    setTitle(src?.title ?? "");
    setAbst(src?.abstract ?? "");
    setThreatImpact(src?.threat_impact ?? 4);
    setTagIds(
      src?.tags
        ? src.tags.map((tag) => tag.tag_id)
        : presetParentTagId
          ? [presetParentTagId]
          : presetTagId
            ? [presetTagId]
            : [],
    );
    setMispTags(src?.misp_tags?.map((misp_tag) => misp_tag.tag_name).join(",") ?? "");
    setActionTagOptions([
      ...new Set([
        ...(src?.tags?.map((tag) => tag.tag_id) ?? []),
        ...(presetParentTagId ? [presetParentTagId] : []),
        ...(presetTagId ? [presetTagId] : []),
      ]),
    ]);
    setActions(presetActions ?? []);
    setEditActionOpen(false);
    setEditActionTarget({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!pteamId || !allTags) return <></>;

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const createActionTagOptions = (tagIdList) => {
    return [
      ...new Set([
        ...tagIdList,
        ...(presetParentTagId ? [presetParentTagId] : []),
        ...(presetTagId ? [presetTagId] : []),
      ]),
    ];
  };

  const validateActionTags = () => {
    const validTagNames = new Set();
    const presetTag = allTags.find((tag) => tag.tag_id === presetTagId);
    validTagNames.add(presetTag.tag_name);

    allTags
      .filter((tag) => tagIds.includes(tag.tag_id))
      .forEach((tag) => {
        validTagNames.add(tag.tag_name);
        if (tag.parent_name && tag.parent_name !== tag.tag_name) {
          validTagNames.add(tag.parent_name);
        }
      });
    for (let action of actions) {
      if (action.ext?.tags && !action.ext.tags.every((tag) => validTagNames.has(tag))) {
        enqueueSnackbar(`Some of the ActionTags "${action.ext.tags}" are not TopicTags`, {
          variant: "error",
        });
        return false;
      }
    }
    return true;
  };

  const reloadTopicAfterAPI = async () => {
    // fix topic state
    await Promise.all([
      dispatch(getTopic(topicId)),
      dispatch(getPTeamTopicActions({ pteamId: pteamId, topicId: topicId })),
      dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId })),
      dispatch(getPTeamTagsSummary({ pteamId: pteamId })),
    ]);
    // update only if needed
    if (pteamId && presetTagId) {
      await Promise.all([
        dispatch(
          getPTeamServiceTaggedTopicIds({
            pteamId: pteamId,
            serviceId: serviceId,
            tagId: presetTagId,
          }),
        ),
      ]);
    }
  };

  const handleCreateTopic = async () => {
    if (!validateActionTags()) return;
    const data = {
      title: title,
      abstract: abst,
      threat_impact: parseInt(threatImpact),
      tags: allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
      misp_tags: mispTags?.length > 0 ? mispTags.split(",").map((mispTag) => mispTag.trim()) : [],
      actions: actions.map((action) => {
        const obj = {
          ...action,
        };
        return obj;
      }),
    };
    await createTopic(topicId, data)
      .then(async () => {
        enqueueSnackbar("Create topic succeeded", { variant: "success" });
        reloadTopicAfterAPI();
        onSetOpen(false);
      })
      .catch((error) => operationError(error));
  };

  const handleUpdateTopic = () => {
    if (!validateActionTags()) return;

    const presetActionIds = new Set(presetActions.map((a) => a.action_id));

    function getNeedUpdateTopic() {
      const presetMispTag = src?.misp_tags?.map((misp_tag) => misp_tag.tag_name).join(",");

      const presetTag = src?.tags
        ? src.tags.map((tag) => tag.tag_id)
        : presetParentTagId
          ? [presetParentTagId]
          : presetTagId
            ? [presetTagId]
            : [];

      const presetData = {
        title: src?.title ?? "",
        abstract: src?.abstract ?? "",
        threat_impact: src?.threat_impact ?? 4,
        tags: allTags.filter((tag) => presetTag.includes(tag.tag_id)).map((tag) => tag.tag_name),
        misp_tags:
          presetMispTag?.length > 0
            ? presetMispTag.split(",").map((mispTag) => mispTag.trim())
            : [],
      };

      return JSON.stringify(data) !== JSON.stringify(presetData) && src.created_by === user.user_id;
    }

    function getNeedUpdateAction(currentActionIds, presetActionIdsArray) {
      if (!arrayComparison(currentActionIds, presetActionIdsArray)) return true;

      for (let i = 0; i < actions.length; i++) {
        if (actions[i].recommended !== presetActions[i].recommended) {
          return true;
        }
      }
      return false;
    }

    async function updateTopicPromise() {
      return updateTopic(topicId, data).catch((error) => operationError(error));
    }

    async function updateActionPromise() {
      let promiseArray = [];
      for (let action of actions) {
        const actionRequest = {
          ...action,
          topic_id: topicId,
        };
        if (action.action_id === null) {
          promiseArray.push(createAction(actionRequest).catch((error) => operationError(error)));
        } else if (presetActionIds.has(action.action_id)) {
          presetActionIds.delete(action.action_id);
          promiseArray.push(
            updateAction(action.action_id, actionRequest).catch((error) => operationError(error)),
          );
        }
      }

      // delete actions that are not related to topic
      for (let actionId of presetActionIds) {
        promiseArray.push(deleteAction(actionId).catch((error) => operationError(error)));
      }
      if (src.created_by !== user.user_id) {
        enqueueSnackbar(
          "Only actions have been changed, not topics. You can't update topic, because you are not topic creator.",
          { variant: "warning" },
        );
      }
      return Promise.all(promiseArray);
    }

    const data = {
      title: title,
      abstract: abst,
      threat_impact: parseInt(threatImpact),
      tags: allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
      misp_tags: mispTags?.length > 0 ? mispTags.split(",").map((mispTag) => mispTag.trim()) : [],
    };

    const currentActionIds = actions.map((action) => action.action_id);
    const presetActionIdsArray = [...presetActionIds];

    const needUpdateAction = getNeedUpdateAction(currentActionIds, presetActionIdsArray);
    const needUpdateTopic = getNeedUpdateTopic();

    if (needUpdateAction) {
      if (needUpdateTopic) {
        Promise.all([updateActionPromise(), updateTopicPromise()]).then(() => {
          reloadTopicAfterAPI();
          enqueueSnackbar("Update topic and action succeeded", { variant: "success" });
          onSetOpen(false);
        });
      } else {
        updateActionPromise().then(() => {
          reloadTopicAfterAPI();
          enqueueSnackbar("Update action succeeded", { variant: "success" });
          onSetOpen(false);
        });
      }
    } else {
      if (needUpdateTopic) {
        updateTopicPromise().then(() => {
          reloadTopicAfterAPI();
          enqueueSnackbar("Update topic succeeded", { variant: "success" });
          onSetOpen(false);
        });
      }
    }
  };

  const handleFetchFlashsense = async () => {
    let newSkipped = skipped;
    if (isStepSkipped(activeStep)) {
      newSkipped = new Set(newSkipped.values());
      newSkipped.delete(activeStep);
    }

    if (!validateUUID(topicId)) {
      setValidErrorMessage("Invalid UUID");
      return;
    }

    await fetchFlashsense(topicId)
      .then((response) => {
        setAbst(response.data?.abstract ?? "");
        setActions(response.data?.actions ?? []);
        setValidErrorMessage("");
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        setSkipped(newSkipped);
      })
      .catch((error) => {
        operationError(error);
        setValidErrorMessage("Something went wrong");
      });
  };

  const isStepOptional = (step) => {
    return step === 0;
  };

  const isStepSkipped = (step) => {
    return skipped.has(step);
  };

  const handleBackFlashsense = () => {
    setValidErrorMessage("");
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    const prevTopicId = presetTopicId ?? "";
    if (skipped.has(0)) {
      setTopicId(prevTopicId);
    }
  };

  const execSkip = () => {
    // Clear error message
    setValidErrorMessage("");

    // Change next step
    setActiveStep((prevActiveStep) => prevActiveStep + 1);

    // Add this step to skip
    setSkipped((prevSkipped) => {
      const newSkipped = new Set(prevSkipped.values());
      newSkipped.add(activeStep);
      return newSkipped;
    });
  };

  const handleSkipFlashsense = () => {
    execSkip();

    if (presetTopicId) {
      // Revert Topic ID to Preset
      setTopicId(presetTopicId);
    } else if (!presetTopicId) {
      setTopicId(uuid.v4());
    }
  };

  const handleClose = () => {
    setActiveStep(presetTopicId ? 1 : 0);
    onSetOpen(false);
  };

  const handleDeleteTopic = () => {
    if (presetTagId) {
      dispatch(
        getPTeamServiceTaggedTopicIds({
          pteamId: pteamId,
          serviceId: serviceId,
          tagId: presetTagId,
        }),
      );
    }
    dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId }));
    dispatch(getPTeamTagsSummary({ pteamId: pteamId }));
  };

  function ActionGeneratorModal() {
    const [generatorOpen, setGeneratorOpen] = useState(false);
    return (
      <>
        <IconButton onClick={() => setGeneratorOpen(true)} sx={{ color: blue[700] }}>
          <AddBoxIcon />
        </IconButton>
        <Dialog open={generatorOpen} onClose={() => setGeneratorOpen(false)}>
          <DialogContent>
            <ActionGenerator
              text="Add action"
              tagIds={actionTagOptions}
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

  function TopicTagSelectorModal(props) {
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
              onApply={(ary) => {
                setTagIds(ary);
                setActionTagOptions(createActionTagOptions(ary));
                setTagOpen(false);
              }}
            />
          </DialogContent>
        </Dialog>
      </>
    );
  }

  const updateErrors = (key, value, validator) => {
    if (validator(value)) setErrors(errors.filter((error) => error !== key));
    else if (errors.indexOf(key) < 0) setErrors([...errors, key]);
  };

  return (
    <>
      <Dialog
        open={open === true}
        onClose={(event, reason) => {
          if (reason && reason === "backdropClick") return;
          onSetOpen(false);
        }}
        maxWidth="md"
        fullWidth
        sx={{ maxHeight: "100vh" }}
      >
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              {presetTopicId ? "Edit Topic" : "Create Topic"}
            </Typography>
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label, index) => {
              const stepProps = {};
              const labelProps = {};
              if (isStepSkipped(index)) {
                stepProps.completed = false;
              }
              return (
                <Step key={label} {...stepProps}>
                  <StepLabel {...labelProps}>{label}</StepLabel>
                </Step>
              );
            })}
          </Stepper>
          <>
            {activeStep === 0 && (
              <Box display="flex" flexDirection="column">
                <Typography sx={{ mt: 2, mb: 1 }}>Import from Flashsense</Typography>
                <TextField
                  size="small"
                  required
                  variant="outlined"
                  value={topicId}
                  placeholder="Please enter UUID"
                  onChange={(event) => {
                    setTopicId(event.target.value);
                  }}
                  error={!validateUUID(topicId)}
                  sx={{ mb: 2, mr: 1, minWidth: "360px" }}
                />
                {validErrorMessage && (
                  <Typography variant="subtitle2" sx={{ color: "error.main" }}>
                    {validErrorMessage}
                  </Typography>
                )}
              </Box>
            )}
            {activeStep === 1 && (
              <Box display="flex" flexDirection="column" m={1}>
                {/* <Box display="flex" flexDirection="column" m={1}> */}
                <Box display="flex" flexDirection="row" mb={1}>
                  <Box mr={2} sx={{ width: "50%" }}>
                    <Typography sx={{ fontWeight: 900 }} mb={1}>
                      Title
                    </Typography>
                    <TextField
                      size="small"
                      required
                      variant="outlined"
                      value={title}
                      onChange={(event) => {
                        setTitle(event.target.value);
                        updateErrors("title", event.target.value, validateNotEmpty);
                      }}
                      error={!validateNotEmpty(title)}
                      // sx={{ minWidth: "450px" }}
                      sx={{ width: "100%" }}
                    />
                  </Box>
                  <Box>
                    <Typography sx={{ fontWeight: 900 }} mb={2}>
                      Topic ID(UUID)
                    </Typography>
                    <Typography>{topicId}</Typography>
                  </Box>
                </Box>
                <Box mb={1}>
                  <Typography sx={{ fontWeight: 900 }} mb={1}>
                    Abstract
                  </Typography>
                  <TextField
                    size="small"
                    multiline
                    variant="outlined"
                    value={abst}
                    onChange={(event) => {
                      setAbst(event.target.value);
                    }}
                    // sx={{ minWidth: "830px" }}
                    sx={{ width: "99%" }}
                  />
                </Box>
                <Box mb={1}>
                  <Typography sx={{ fontWeight: 900 }} mb={1}>
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
                </Box>
                <Box mb={1}>
                  <Box display="flex" flexDirection="row" alignItems="center" mb={1}>
                    <Typography sx={{ fontWeight: 900 }}>Actions</Typography>
                    <ActionGeneratorModal />
                  </Box>
                  {actions?.length > 0 || (
                    <Box
                      display="flex"
                      flexDirection="row"
                      alignItems="center"
                      sx={{ color: grey[500] }}
                    >
                      <ContentPasteIcon fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2">Please add action</Typography>
                    </Box>
                  )}
                  <List
                    sx={{
                      width: "98%",
                      position: "relative",
                      overflow: "auto",
                      maxHeight: 200,
                    }}
                  >
                    {actions
                      .slice()
                      .sort(
                        (a, b) =>
                          actionTypes.indexOf(a.action_type) - actionTypes.indexOf(b.action_type),
                      )
                      .map((action, idx) => (
                        <ActionItem
                          key={idx}
                          action={action.action}
                          actionId={action.action_id}
                          actionType={action.action_type}
                          recommended={action.recommended}
                          ext={action.ext}
                          onChangeRecommended={() =>
                            setActions(
                              actions.map((item) =>
                                item !== action
                                  ? item
                                  : { ...item, recommended: !item.recommended },
                              ),
                            )
                          }
                          onDelete={() => setActions(actions.filter((item) => item !== action))}
                          sx={{ flexGrow: 1 }}
                        />
                      ))}
                  </List>
                </Box>
                <Box mb={1}>
                  <Box mb={1}>
                    <Box display="flex" flexDirection="row" alignItems="center">
                      <Typography sx={{ fontWeight: 900 }}>Artifact Tags</Typography>
                      <TopicTagSelectorModal />
                    </Box>
                    <TextField
                      size="small"
                      variant="outlined"
                      value={allTags
                        .filter((tag) => tagIds.includes(tag.tag_id))
                        .map((tag) => tag.tag_name)
                        .join(", ")}
                      // sx={{ minWidth: "830px" }}
                      sx={{ width: "99%" }}
                      inputProps={{ readOnly: true }}
                    />
                  </Box>
                  <Box>
                    <Typography sx={{ fontWeight: 900, mt: "7px", mb: 1.7 }}>
                      Misp Tags (CSV)
                    </Typography>
                    <TextField
                      size="small"
                      variant="outlined"
                      value={mispTags}
                      onChange={(event) => setMispTags(event.target.value)}
                      // sx={{ minWidth: "720px" }}
                      sx={{ width: "99%" }}
                    />
                  </Box>
                </Box>
                {/* </Box> */}
              </Box>
            )}
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBackFlashsense}
                className={dialogStyle.submit_btn}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />
              {isStepOptional(activeStep) && (
                <Button onClick={handleSkipFlashsense} className={dialogStyle.submit_btn}>
                  Skip
                </Button>
              )}
              {activeStep === steps.length - 1 ? (
                <Button
                  onClick={
                    presetTopicId && topicId === presetTopicId
                      ? handleUpdateTopic
                      : handleCreateTopic
                  }
                  disabled={errors?.length > 0}
                  className={dialogStyle.submit_btn}
                >
                  {presetTopicId && topicId === presetTopicId ? "Update" : "Create"}
                </Button>
              ) : (
                <Button
                  onClick={handleFetchFlashsense}
                  disabled={!topicId}
                  className={dialogStyle.submit_btn}
                >
                  Next
                </Button>
              )}
            </Box>
            {activeStep === 1 && presetTopicId && (
              <Box mb={1}>
                <Divider sx={{ my: 5 }} />
                <Typography sx={{ fontWeight: 900, color: "error.main" }} mb={1}>
                  Delete Topic
                </Typography>
                <Box display="flex" flexDirection="row" alignItems="center">
                  <Typography variant="body2" mb={1} mr={2}>
                    Once you delete topic, there is no going back.
                  </Typography>
                  <TopicDeleteModal
                    topicId={presetTopicId}
                    onSetOpenTopicModal={onSetOpen}
                    onDelete={handleDeleteTopic}
                  />
                </Box>
              </Box>
            )}
          </>
        </DialogContent>
      </Dialog>
      <Dialog open={editActionOpen} onClose={() => setEditActionOpen(false)}>
        <DialogContent>
          <ActionGenerator
            text="Update action"
            tagIds={actionTagOptions}
            action={editActionTarget}
            onEdit={(ret) => {
              setActions(actions.map((item) => (item !== editActionTarget ? item : ret)));
              setEditActionOpen(false);
            }}
            onCancel={() => setEditActionOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

TopicModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  presetTopicId: PropTypes.string,
  presetTagId: PropTypes.string,
  presetParentTagId: PropTypes.string,
  presetActions: PropTypes.arrayOf(
    PropTypes.shape({
      action_id: PropTypes.string,
      action: PropTypes.string,
      action_type: PropTypes.string,
      recommended: PropTypes.bool,
      ext: PropTypes.shape({
        tags: PropTypes.array,
        vulnerable_versions: PropTypes.object,
      }),
    }),
  ),
  serviceId: PropTypes.string.isRequired,
};
