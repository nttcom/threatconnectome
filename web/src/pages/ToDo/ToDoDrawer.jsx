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
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useState } from "react";

import { ActionTypeIcon } from "../../components/ActionTypeIcon";
import { PackageView } from "../../components/PackageView";
import { createActionByFixedVersions, findMatchedVulnPackage } from "../../utils/vulnUtils.js";
import { AssigneesSelector } from "../Package/VulnTables/AssigneesSelector.jsx";
import { SafetyImpactSelector } from "../Package/VulnTables/SafetyImpactSelector.jsx";
import { VulnStatusSelector } from "../Package/VulnTables/VulnStatusSelector.jsx";

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
  const {
    open,
    setOpen,
    row,
    pteamName,
    serviceName,
    pteamMembers,
    serviceDependency,
    vuln,
    vulnActions,
    bgcolor,
  } = props;
  const [value, setValue] = useState(0);

  const currentPackage = {
    package_name: serviceDependency.package_name,
    package_source_name: serviceDependency.package_source_name,
    vuln_matching_ecosystem: serviceDependency.vuln_matching_ecosystem,
  };
  const vulnerablePackage = findMatchedVulnPackage(vuln.vulnerable_packages, currentPackage);
  const affectedVersions = vulnerablePackage?.affected_versions ?? [];
  const patchedVersions = vulnerablePackage?.fixed_versions ?? [];
  const actionByFixedVersions = createActionByFixedVersions(
    affectedVersions,
    patchedVersions,
    vulnerablePackage?.affected_name,
  );

  const actions = [actionByFixedVersions, ...(Array.isArray(vulnActions) ? vulnActions : [])];

  const handleChange = (event, newValue) => {
    setValue(newValue);
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
              <Typography>{pteamName || "-"}</Typography>
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Service
              </Typography>
              <Typography>{serviceName || "-"}</Typography>
              <IconButton size="small">
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Package
              </Typography>
              <Typography>
                {vulnerablePackage
                  ? `${vulnerablePackage.affected_name} : ${vulnerablePackage.ecosystem}`
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
              <Typography>{serviceDependency.target || "-"}</Typography>
            </Box>
            <Box sx={{ display: "flex" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Safety Impact
              </Typography>
              <FormControl sx={{ width: 130 }} size="small" variant="standard">
                <SafetyImpactSelector
                  pteamId={row.pteam_id}
                  ticket={{
                    ticket_id: row.ticket_id,
                    ticket_safety_impact: row.ticket_safety_impact || null,
                    ticket_safety_impact_change_reason:
                      row.ticket_safety_impact_change_reason || null,
                  }}
                />
              </FormControl>
            </Box>
            <Box sx={{ display: "flex" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Status
              </Typography>
              <FormControl sx={{ width: 130 }} size="small" variant="standard">
                <VulnStatusSelector
                  pteamId={row.pteam_id}
                  serviceId={row.service_id}
                  vulnId={row.vuln_id}
                  packageId={serviceDependency.package_id}
                  ticketId={row.ticket_id}
                  currentStatus={row.ticket_status}
                  actionByFixedVersions={actionByFixedVersions}
                  vulnActions={vulnActions}
                />
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
                <AssigneesSelector
                  key={row.assignee || ""}
                  pteamId={row.pteam_id}
                  serviceId={row.service_id}
                  vulnId={row.vuln_id}
                  packageId={serviceDependency.package_id}
                  ticketId={row.ticket_id}
                  currentAssigneeIds={
                    row.assignee && row.assignee !== "-"
                      ? row.assignee.split(",").map((id) => id.trim())
                      : []
                  }
                  members={pteamMembers}
                />
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
              {vulnerablePackage ? (
                <PackageView vulnPackage={vulnerablePackage} />
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
  pteamName: PropTypes.string,
  serviceName: PropTypes.string,
  pteamMembers: PropTypes.object,
  assigneeEmails: PropTypes.string,
  serviceDependency: PropTypes.object.isRequired,
  vuln: PropTypes.object,
  vulnActions: PropTypes.array,
  bgcolor: PropTypes.string.isRequired,
};
