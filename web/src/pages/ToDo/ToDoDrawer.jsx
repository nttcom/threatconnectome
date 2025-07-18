import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Card,
  Chip,
  Drawer,
  FormControl,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useState } from "react";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth.js";
import { useGetPTeamMembersQuery } from "../../services/tcApi.js";

import { ActionTypeIcon } from "../../components/ActionTypeIcon";
import { PackageView } from "../../components/PackageView";
import { createActionByFixedVersions } from "../../utils/vulnUtils.js";

function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

export function ToDoDrawer(props) {
  const { open, setOpen, row, service, dependency, vuln, vulnActions, bgcolor } = props;
  const [value, setValue] = useState(0);
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const packageId = dependency?.package_id;
  const matchedVulnPackage = vuln?.vulnerable_packages.find((pkg) => pkg.package_id === packageId);
  const affectedVersions = matchedVulnPackage?.affected_versions ?? [];
  const patchedVersions = matchedVulnPackage?.fixed_versions ?? [];
  const actionByFixedVersions = createActionByFixedVersions(
    affectedVersions,
    patchedVersions,
    matchedVulnPackage?.name ?? "",
  );
  const actions = [actionByFixedVersions, ...(Array.isArray(vulnActions) ? vulnActions : [])];
  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(row?.pteam_id, { skip: skipByAuth });

  const memberList = Array.isArray(members) ? members : members ? Object.values(members) : [];

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const handleAssigneesChange = (event) => {
    const {
      target: { value },
    } = event;
    setAssignees(typeof value === "string" ? value.split(",") : value);
  };

  return (
    <Drawer anchor="right" open={open} onClose={() => setOpen(false)}>
      <Box>
        <Tooltip arrow title="Close">
          <IconButton size="large" onClick={() => setOpen(false)}>
            <KeyboardDoubleArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ width: 800, px: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ pb: 1, fontWeight: "bold" }}>
            Ticket #{row?.ticket_id || ""}
          </Typography>
        </Box>
        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
          <Tabs value={value} onChange={handleChange}>
            <Tab label="Ticket" />
            <Tab label="Vuln" />
          </Tabs>
        </Box>
        {/* ticket */}
        <CustomTabPanel value={value} index={0}>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                SSVC
              </Typography>
              <Chip label={row?.ssvc || "-"} sx={{ backgroundColor: bgcolor, color: "#fff" }} />
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                CVE ID
              </Typography>
              {vuln?.cve_id === null ? (
                <Typography>No Known CVE</Typography>
              ) : (
                <Typography>{vuln?.cve_id || "-"}</Typography>
              )}
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Team
              </Typography>
              <Typography>{row?.team || "-"}</Typography>
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Service
              </Typography>
              <Typography>{service?.service_name || "-"}</Typography>
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Package
              </Typography>
              <Typography>
                {matchedVulnPackage
                  ? `${matchedVulnPackage.name} : ${matchedVulnPackage.ecosystem}`
                  : "-"}
              </Typography>
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Target
              </Typography>
              <Typography>{dependency?.target || "-"}</Typography>
            </Box>
            <Box sx={{ display: "flex" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Safety Impact
              </Typography>
              <FormControl sx={{ width: 130 }} size="small" variant="standard">
                <Select defaultValue="Negligible">
                  <MenuItem value="Negligible">Negligible</MenuItem>
                  <MenuItem value="Marginal">Marginal</MenuItem>
                  <MenuItem value="Critical">Critical</MenuItem>
                  <MenuItem value="Catastrophic">Catastrophic</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Box sx={{ display: "flex" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Status
              </Typography>
              <FormControl sx={{ width: 130 }} size="small" variant="standard">
                <Select defaultValue="Alerted">
                  <MenuItem value="Alerted">Alerted</MenuItem>
                  <MenuItem value="Acknowledged">Acknowledged</MenuItem>
                  <MenuItem value="Scheduled">Scheduled</MenuItem>
                  <MenuItem value="Completed">Completed</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Due date
              </Typography>
              <Typography>{row?.dueDate}</Typography>
            </Box>
            <Box sx={{ display: "flex" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Assignees
              </Typography>
              <FormControl sx={{ width: 200 }} size="small" variant="standard">
                <Select
                  defaultValue={row?.assignee ? row.assignee.split(",").map((s) => s.trim()) : []}
                  multiple
                  onChange={handleAssigneesChange}
                >
                  {memberList.map((member) => (
                    <MenuItem key={member.email} value={member.email}>
                      {member.email}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </Stack>
        </CustomTabPanel>

        {/* vuln */}
        <CustomTabPanel value={value} index={1}>
          <Stack spacing={1}>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                Package
              </Typography>
              {matchedVulnPackage ? (
                <PackageView vulnPackage={matchedVulnPackage} />
              ) : (
                <Typography color="text.secondary">No package data</Typography>
              )}
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                Mitigations
              </Typography>
              <Card variant="outlined" sx={{ m: 1, p: 2 }}>
                <List>
                  {actions.length === 0 ? (
                    <ListItem>
                      <ListItemText primary={"No data"} />
                    </ListItem>
                  ) : (
                    actions
                      .filter((action) => action)
                      .map((action) => (
                        <ListItem key={action.action_id}>
                          <ListItemIcon>
                            <ActionTypeIcon
                              actionType={action.action_type}
                              disabled={!action.recommended}
                            />
                          </ListItemIcon>
                          <ListItemText primary={action.action} />
                        </ListItem>
                      ))
                  )}
                </List>
              </Card>
            </Box>
            <Box>
              <Typography variant="h6" sx={{ width: 170 }}>
                CVE ID
              </Typography>
              {vuln?.cve_id === null ? (
                <Typography sx={{ margin: 1 }}>No Known CVE</Typography>
              ) : (
                <Box>{vuln?.cve_id && <Chip label={vuln.cve_id} sx={{ m: 1 }} />}</Box>
              )}
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                Detail
              </Typography>
              <Card variant="outlined" sx={{ m: 1, p: 2 }}>
                <Typography variant="body1">{vuln?.detail}</Typography>
              </Card>
            </Box>
          </Stack>
        </CustomTabPanel>
      </Box>
    </Drawer>
  );
}

ToDoDrawer.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired,
  row: PropTypes.object.isRequired,
  service: PropTypes.object,
  dependency: PropTypes.object,
  vuln: PropTypes.object,
  vulnActions: PropTypes.array,
  bgcolor: PropTypes.string.isRequired,
};
