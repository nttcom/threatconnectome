import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  SentimentSatisfiedAlt as SentimentSatisfiedAltIcon,
  SentimentVeryDissatisfied as SentimentVeryDissatisfiedIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Stepper,
  Step,
  StepButton,
  TextField,
  Typography,
  List,
} from "@mui/material";
import { blue, red, green } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import uuid from "react-native-uuid";
import { useDispatch, useSelector } from "react-redux";

import dialogStyle from "../cssModule/dialog.module.css";
import { getATeamTopics } from "../slices/ateam";
import { getTopic } from "../slices/topics";
import { createTopic } from "../utils/api";
import { actionTypes } from "../utils/const";
import { pickMismatchedTopicActionTags, validateNotEmpty, validateUUID } from "../utils/func";

import { ActionGenerator } from "./ActionGenerator";
import { ActionItem } from "./ActionItem";
import { ThreatImpactChip } from "./ThreatImpactChip";
import { TopicTagSelector } from "./TopicTagSelector";

const steps = ["Threat, Vulnerability, and Risk", "Dissemination", "Response planning"];

export function ATeamTopicCreateModal(props) {
  const { open, onSetOpen } = props;

  const [activeStep, setActiveStep] = useState(0);
  const [topicId, setTopicId] = useState(uuid.v4());
  const [title, setTitle] = useState("");
  const [abst, setAbst] = useState("");
  const [threatImpact, setThreatImpact] = useState(1);
  const [tagIds, setTagIds] = useState([]);
  const [actions, setActions] = useState([]);
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [editActionOpen, setEditActionOpen] = useState(false);
  const [editActionTarget] = useState({});

  const ateamId = useSelector((state) => state.ateam.ateamId); // dispatched by parent
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  const resetParams = () => {
    setActiveStep(0);
    setTopicId(uuid.v4());
    setTitle("");
    setAbst("");
    setThreatImpact(1);
    setTagIds([]);
    setActions([]);
  };

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const validateTopicParams = () => validateUUID(topicId) && validateNotEmpty(title);

  const createActionTagOptions = (tagIdList) => {
    // TODO
    return [];
  };

  const validateActionTags = () => {
    const topicTagNames = allTags
      .filter((tag) => tagIds.includes(tag.tag_id))
      .map((tag) => tag.tag_name);
    const actionTagNames = [
      ...new Set(actions.reduce((ret, action) => [...ret, ...(action.ext?.tags ?? [])], [])),
    ];
    const mismatchedTagNames = pickMismatchedTopicActionTags(topicTagNames, actionTagNames);
    if (mismatchedTagNames.length > 0) {
      for (let mismatchedTagName of mismatchedTagNames) {
        enqueueSnackbar(`ActionTag: ${mismatchedTagName} is not related on TopicTags`, {
          variant: "error",
        });
      }
      return false;
    }
    return true;
  };

  const handleCreateTopic = async () => {
    if (!validateActionTags()) return;
    const data = {
      title: title,
      abstract: abst,
      threat_impact: parseInt(threatImpact),
      tags: allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
      actions: actions.map((action) => {
        const obj = {
          ...action,
        };
        return obj;
      }),
    };
    await createTopic(topicId, data)
      .then(async (response) => {
        // fix topic state
        await Promise.all([
          enqueueSnackbar("Create topic succeeded", { variant: "success" }),
          dispatch(getTopic(topicId)),
          dispatch(getATeamTopics(ateamId)),
        ]);
      })
      .catch((error) => operationError(error));
    resetParams();
    onSetOpen(false);
  };

  const handleNext = () => setActiveStep(activeStep + 1);

  const handleBack = () => setActiveStep(activeStep - 1);

  const createStepHandler = (step) => () => setActiveStep(step);

  const handleClose = () => {
    resetParams();
    onSetOpen(false);
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

  return (
    <>
      <Dialog
        open={open === true}
        onClose={(event, reason) => {
          if (reason === "backdropClick") return;
          onSetOpen(false);
        }}
        maxWidth="md"
        fullWidth
        sx={{ maxHeight: "100vh" }}
      >
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              Create Topic
            </Typography>
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stepper nonLinear activeStep={activeStep} alternativeLabel>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepButton color="inherit" onClick={createStepHandler(index)}>
                  {label}
                </StepButton>
              </Step>
            ))}
          </Stepper>
          <>
            {activeStep === 0 && (
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
                  // sx={{ minWidth: "400px" }}
                  sx={{ width: "100%" }}
                />
                <Typography variant="body2" sx={{ fontWeight: 600, mt: 2 }}>
                  Topic ID(UUID)
                </Typography>
                <TextField
                  size="small"
                  required
                  variant="outlined"
                  value={topicId}
                  error={!validateUUID(topicId)}
                  onChange={(event) => setTopicId(event.target.value)}
                />
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
                    // sx={{ minWidth: "480px" }}
                    sx={{ width: "100%" }}
                  />
                  {abst === "" ? (
                    <SentimentVeryDissatisfiedIcon sx={{ color: red[600], mt: 9, ml: 1 }} />
                  ) : (
                    <SentimentSatisfiedAltIcon sx={{ color: green[600], mt: 9, ml: 1 }} />
                  )}
                </Box>
              </Box>
            )}
            {activeStep === 1 && (
              <Box display="flex" flexDirection="column" sx={{ m: 2 }}>
                <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Artifact Tag
                  </Typography>
                  <TopicTagSelectorModal />
                </Box>
                <TextField
                  size="small"
                  variant="outlined"
                  value={allTags
                    .filter((tag) => tagIds.includes(tag.tag_id))
                    .map((tag) => tag.tag_name)
                    .join(", ")}
                  // sx={{ minWidth: "720px" }}
                  sx={{ width: "100%" }}
                  inputProps={{ readOnly: true }}
                />
                <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    The PTeam that the topic reaches
                  </Typography>
                </Box>
              </Box>
            )}
            {activeStep === 2 && (
              <Box sx={{ m: 2 }}>
                <Box display="flex" flexDirection="row" alignItems="center" mb={1}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Action
                  </Typography>
                  <ActionGeneratorModal />
                </Box>
                <List
                  sx={{
                    width: "100%",
                    position: "relative",
                    overflow: "auto",
                    maxHeight: 150,
                  }}
                >
                  {actions
                    .slice()
                    .sort(
                      (a, b) =>
                        actionTypes.indexOf(a.action_type) - actionTypes.indexOf(b.action_type),
                    )
                    .map((action, idx) => (
                      <>
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
                      </>
                    ))}
                </List>
              </Box>
            )}
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                className={dialogStyle.submit_btn}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />
              {activeStep === steps.length - 1 ? (
                <Button
                  onClick={handleCreateTopic}
                  disabled={!validateTopicParams()}
                  className={dialogStyle.submit_btn}
                >
                  Create
                </Button>
              ) : (
                <Button onClick={handleNext} className={dialogStyle.submit_btn}>
                  Next
                </Button>
              )}
            </Box>
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

ATeamTopicCreateModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
};
