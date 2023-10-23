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
import PropTypes from "prop-types";
import React, { useState } from "react";
import uuid from "react-native-uuid";

import TabPanel from "../components/TabPanel";
import { modalCommonButtonStyle } from "../utils/const";
import { validateNotEmpty, a11yProps } from "../utils/func";

import ActionGenerator from "./ActionGenerator";
import ActionTypeIcon from "./ActionTypeIcon";
import ThreatImpactChip from "./ThreatImpactChip";
import TopicTagSelector from "./TopicTagSelector";
import { ZoneSelectorModal } from "./ZoneSelectorModal";

// sample data
const sample_tag = [
  {
    name: "../../../../pkg:golang:",
  },
  {
    name: "../../:golang",
  },
  {
    name: "mlflow:pypi:",
  },
];

const sample_zone = [
  {
    name: "testzone1",
  },
  {
    name: "testzone2",
  },
  {
    name: "testzone3",
  },
];

const sample_action = [
  {
    action: "Update test to version 0.7.19",
    actionId: "98097879-985a- 44ad - 9443 - 5d465a068c94",
    actionType: "elimination",
    author: "tanaka taro",
    createDate: "2023/8/10",
    recommended: true,
    different: true,
    zones: ["zone1", "zone2", "zone3"],
    ext: {
      tags: ["mlflow:pypi:"],
      vulnerable_versions: {},
    },
    focusTags: null,
  },
  {
    action: "Update 8.10",
    actionId: "98097879-985a- 44ad - 9443 - 5d465a068c95",
    actionType: "detection",
    author: "tanaka taro",
    createDate: "2023/8/10",
    recommended: true,
    different: false,
    zones: ["zone4", "zone5", "zone6"],
    ext: {
      tags: ["mlflow:pypi:"],
      vulnerable_versions: {},
    },
    focusTags: null,
  },
  {
    action: "Update test0727 to version 111",
    actionId: "2fb5c256-6ff1-4382-8928-1e67751a03c3",
    actionType: "acceptance",
    author: "tanaka taro",
    createDate: "2023/8/10",
    recommended: false,
    different: true,
    zones: [],
    ext: {
      tags: [],
      vulnerable_versions: {},
    },
    focusTags: null,
  },
];

export default function TopicEditModal(props) {
  const { open, setOpen } = props;
  const [title, setTitle] = useState("");
  const [topicId] = useState(uuid.v4());
  const [threatImpact, setThreatImpact] = useState(1);
  const [abst, setAbst] = useState("");
  const [actions, setActions] = useState([]);
  const [zoneNames, setZoneNames] = useState([]);
  const [zonesRelatedTeams] = useState({ ateams: {}, pteams: {} });
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [tagIds, setTagIds] = useState([]);
  const [tab, setTab] = useState(0);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const handleClose = () => {
    setOpen(false);
  };

  const createActionTagOptions = (tagIdList) => {
    // TODO
    return [];
  };

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
                {sample_tag.map((tag) => (
                  <Box key={tag.name}>
                    <ListItem
                      key={tag.name}
                      disablePadding
                      secondaryAction={
                        <IconButton edge="end" aria-label="delete">
                          <DeleteIcon />
                        </IconButton>
                      }
                    >
                      <ListItemText
                        primary={tag.name}
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
                    // setZonesRelatedTeams(await collectZonesRelatedTeams(newZoneNames));
                    setZoneNames(newZoneNames.sort());
                  }}
                />
              </Box>
              <List sx={{ ml: 1 }}>
                {sample_zone.map((tag) => (
                  <Box key={tag.name}>
                    <ListItem
                      key={tag.name}
                      disablePadding
                      secondaryAction={
                        <IconButton edge="end" aria-label="delete">
                          <DeleteIcon />
                        </IconButton>
                      }
                    >
                      <ListItemText
                        key={tag.name}
                        primary={tag.name}
                        primaryTypographyProps={{
                          style: {
                            whiteSpace: "nowrap",
                            overflow: "auto",
                            textOverflow: "ellipsis",
                          },
                        }}
                      />
                    </ListItem>
                    <Divider key={tag.name} />
                  </Box>
                ))}
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
              ) : zonesRelatedTeams === undefined ? (
                <Typography sx={{ color: "red" }}>Something went wrong</Typography>
              ) : Object.values(zonesRelatedTeams.pteams).length > 0 ? (
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
              <ActionGeneratorModal />
            </Box>
            <List sx={{ ml: 1 }}>
              {sample_action.map((action) => (
                <Box key={action.action}>
                  <ListItem
                    key={action.action}
                    disablePadding
                    secondaryAction={
                      <IconButton edge="end" aria-label="delete">
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <IconButton sx={{ pb: 0.5 }}>
                      <ActionTypeIcon
                        disabled={!action.recommended}
                        actionType={action.actionType}
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
          <Button sx={modalCommonButtonStyle}>Update</Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

TopicEditModal.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
};
