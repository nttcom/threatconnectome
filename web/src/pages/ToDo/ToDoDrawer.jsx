import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Chip,
  Drawer,
  FormControl,
  IconButton,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { CustomTabPanel } from "../../components/CustomTabPanel.jsx";
import { createActionByFixedVersions, findMatchedVulnPackage } from "../../utils/vulnUtils.js";
import { AssigneesSelector } from "../Package/VulnTables/AssigneesSelector.jsx";
import { SafetyImpactSelector } from "../Package/VulnTables/SafetyImpactSelector.jsx";
import { VulnStatusSelector } from "../Package/VulnTables/VulnStatusSelector.jsx";
import { VulnerabilityView } from "../Vulnerability/VulnerabilityView.jsx";

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
    ssvcPriority,
  } = props;
  const [value, setValue] = useState(0);
  const navigate = useNavigate();

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

  const handleTabChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleCVEClick = () => {
    if (vuln?.vuln_id) {
      navigate(`/vulns/${vuln.vuln_id}?pteamId=${row.pteam_id}&serviceId=${row.service_id}`);
    }
  };

  const handleTeamClick = () => {
    if (row?.pteam_id) {
      navigate(`/pteam?pteamId=${row.pteam_id}&serviceId=${row.service_id}`);
    }
  };

  const handleServiceClick = () => {
    if (row?.pteam_id && row?.service_id) {
      navigate(`/?pteamId=${row.pteam_id}&serviceId=${row.service_id}`);
    }
  };

  const handlePackageClick = () => {
    if (row?.pteam_id && row?.service_id && serviceDependency?.package_id) {
      navigate(
        `/packages/${serviceDependency.package_id}?pteamId=${row.pteam_id}&serviceId=${row.service_id}`,
      );
    }
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
          <Tabs value={value} onChange={handleTabChange}>
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
              <Chip
                label={row?.ssvc || "-"}
                sx={{ backgroundColor: ssvcPriority.style.bgcolor, color: "#fff" }}
              />
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
              <IconButton size="small" onClick={handleCVEClick}>
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Team
              </Typography>
              <Typography>{pteamName || "-"}</Typography>
              <IconButton size="small" onClick={handleTeamClick}>
                <OpenInNewIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Service
              </Typography>
              <Typography>{serviceName || "-"}</Typography>
              <IconButton size="small" onClick={handleServiceClick}>
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
              <IconButton size="small" onClick={handlePackageClick}>
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
              <Typography>{row?.dueDate || "-"}</Typography>
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
                    row.assignee && row.assignee !== "-" ? row.assignee.map((id) => id.trim()) : []
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
            <VulnerabilityView
              vuln={vuln}
              vulnActions={vulnActions}
              currentPackage={currentPackage}
            />
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
  serviceDependency: PropTypes.object.isRequired,
  vuln: PropTypes.object,
  vulnActions: PropTypes.array,
  ssvcPriority: PropTypes.shape({
    icon: PropTypes.elementType.isRequired,
    displayName: PropTypes.string.isRequired,
    style: PropTypes.object.isRequired,
  }).isRequired,
};
