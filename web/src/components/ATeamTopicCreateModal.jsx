import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  FiberManualRecord as FiberManualRecordIcon,
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
  ListItem,
  ListItemText,
} from "@mui/material";
import { blue, grey, red, green } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import uuid from "react-native-uuid";
import { useDispatch, useSelector } from "react-redux";

import { getATeamTopics } from "../slices/ateam";
import { getTopic } from "../slices/topics";
import { createTopic, getZonedTeams } from "../utils/api";
import { actionTypes, modalCommonButtonStyle } from "../utils/const";
import { pickMismatchedTopicActionTags, validateNotEmpty, validateUUID } from "../utils/func";

import { ActionGenerator } from "./ActionGenerator";
import { ActionItem } from "./ActionItem";
import { ThreatImpactChip } from "./ThreatImpactChip";
import { TopicTagSelector } from "./TopicTagSelector";
import { ZoneSelectorModal } from "./ZoneSelectorModal";

const steps = ["Threat, Vulnerability, and Risk", "Dissemination", "Response planning"];

export function ATeamTopicCreateModal(props) {
  const { open, setOpen } = props;

  const [activeStep, setActiveStep] = useState(0);
  const [topicId, setTopicId] = useState(uuid.v4());
  const [title, setTitle] = useState("");
  const [abst, setAbst] = useState("");
  const [threatImpact, setThreatImpact] = useState(1);
  const [tagIds, setTagIds] = useState([]);
  const [zoneNames, setZoneNames] = useState([]);
  const [actions, setActions] = useState([]);
  const [zonesRelatedTeams, setZonesRelatedTeams] = useState({ ateams: {}, pteams: {} });
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [editActionOpen, setEditActionOpen] = useState(false);
  const [editActionTarget, setEditActionTarget] = useState({});

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
    setZoneNames([]);
    setActions([]);
  };

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const validateTopicParams = () =>
    validateUUID(topicId) &&
    validateNotEmpty(title) &&
    (zoneNames.length === 0 ||
      (zonesRelatedTeams !== undefined && Object.values(zonesRelatedTeams.pteams).length > 0));

  const collectZonesRelatedTeams = async (zoneNames) => {
    const emptyResult = { ateams: {}, pteams: {} };
    const solvedData = await Promise.all(
      zoneNames.map((zoneName) => getZonedTeams(zoneName))
    ).catch((error) => {
      operationError(error);
    });
    if (solvedData === undefined) return undefined; // caught error

    return solvedData
      .map((solved) => solved.data)
      .reduce(
        (ret, teamData) => ({
          ...ret,
          ateams: {
            ...ret.ateams,
            ...teamData.ateams.reduce(
              (newATeams, ateam) => ({
                ...newATeams,
                [ateam.ateam_id]: ateam,
              }),
              {}
            ),
          },
          pteams: {
            ...ret.pteams,
            ...teamData.pteams.reduce(
              (newPTeams, pteam) => ({
                ...newPTeams,
                [pteam.pteam_id]: pteam,
              }),
              {}
            ),
          },
        }),
        emptyResult
      );
  };

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
      zone_names: zoneNames,
      actions: actions.map((action) => {
        const obj = {
          ...action,
          zone_names:
            action.zones?.length > 0 && typeof action.zones[0] === "string"
              ? action.zones
              : action.zones.map((zone) => zone.zone_name),
        };
        delete obj.zones;
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
    setOpen(false);
  };

  const handleNext = () => setActiveStep(activeStep + 1);

  const handleBack = () => setActiveStep(activeStep - 1);

  const createStepHandler = (step) => () => setActiveStep(step);

  const handleClose = () => {
    resetParams();
    setOpen(false);
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
          setOpen(false);
        }}
        maxWidth="md"
        fullWidth
        sx={{ maxHeight: "100vh" }}
      >
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
              Create Topic
            </Typography>
            <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
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
                    Zone
                  </Typography>
                  <ZoneSelectorModal
                    currentZoneNames={zoneNames}
                    onApply={async (newZoneNames) => {
                      if (newZoneNames.sort().toString() === zoneNames.toString()) return;
                      setZonesRelatedTeams(await collectZonesRelatedTeams(newZoneNames));
                      setZoneNames(newZoneNames.sort());
                    }}
                  />
                </Box>
                <TextField
                  size="small"
                  variant="outlined"
                  value={zoneNames.join(", ")}
                  error={
                    zoneNames.length > 0 &&
                    (zonesRelatedTeams === undefined ||
                      Object.values(zonesRelatedTeams.pteams).length === 0)
                  }
                  // sx={{ minWidth: "720px" }}
                  sx={{ width: "100%" }}
                  inputProps={{ readOnly: true }}
                />
                <Box display="flex" flexDirection="row" alignItems="center" mt={2}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    The PTeam that the topic reaches
                  </Typography>
                </Box>
                <List sx={{ ml: 1 }}>
                  {zoneNames.length === 0 ? (
                    <>All of PTeams</>
                  ) : zonesRelatedTeams === undefined ? (
                    <Typography sx={{ color: "red" }}>Something went wrong</Typography>
                  ) : Object.values(zonesRelatedTeams.pteams).length > 0 ? (
                    <>
                      {Object.values(zonesRelatedTeams.pteams).map((pteam) => (
                        <ListItem key={pteam.pteam_id} disablePadding>
                          <FiberManualRecordIcon
                            sx={{ m: 1, color: grey[500], fontSize: "small" }}
                          />
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
                    </>
                  ) : (
                    <Typography sx={{ color: "red" }}>No PTeams</Typography>
                  )}
                </List>
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
                {actions
                  .slice()
                  .sort(
                    (a, b) =>
                      actionTypes.indexOf(a.action_type) - actionTypes.indexOf(b.action_type)
                  )
                  .map((action, idx) => (
                    <Box key={idx} display="flex" flexDirection="row" alignItems="center" m={1}>
                      <ActionItem
                        key={idx}
                        action={action.action}
                        actionId={action.action_id}
                        actionType={action.action_type}
                        recommended={action.recommended}
                        zones={action.zones}
                        ext={action.ext}
                        onChangeRecommended={() =>
                          setActions(
                            actions.map((item) =>
                              item !== action ? item : { ...item, recommended: !item.recommended }
                            )
                          )
                        }
                        onDelete={() => setActions(actions.filter((item) => item !== action))}
                        sx={{ flexGrow: 1 }}
                      />
                      <IconButton
                        onClick={() => {
                          setEditActionTarget(action);
                          setEditActionOpen(true);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                    </Box>
                  ))}
              </Box>
            )}
            <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1, textTransform: "none" }}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />
              {activeStep === steps.length - 1 ? (
                <Button
                  onClick={handleCreateTopic}
                  disabled={!validateTopicParams()}
                  sx={modalCommonButtonStyle}
                >
                  Create
                </Button>
              ) : (
                <Button onClick={handleNext} sx={modalCommonButtonStyle}>
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
  setOpen: PropTypes.func.isRequired,
};
