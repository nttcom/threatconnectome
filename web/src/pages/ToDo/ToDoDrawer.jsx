import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import LinkIcon from "@mui/icons-material/Link";
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
import { useNavigate, useLocation } from "react-router-dom";

import { CustomTabPanel } from "../../components/CustomTabPanel.jsx";
import { preserveParams } from "../../utils/urlUtils";
import { createActionByFixedVersions, findMatchedVulnPackage } from "../../utils/vulnUtils.js";
import { AssigneesSelector } from "../Package/VulnTables/AssigneesSelector.jsx";
import { SafetyImpactSelector } from "../Package/VulnTables/SafetyImpactSelector.jsx";
import { TicketHandlingStatusSelector } from "../Package/VulnTables/TicketHandlingStatusSelector.jsx";
import { VulnerabilityView } from "../Vulnerability/VulnerabilityView.jsx";

import { RiskAnalysis } from "./Insights/RiskAnalysis.jsx";

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
  const location = useLocation();

  const currentPackage = {
    package_name: serviceDependency.package_name,
    package_source_name: serviceDependency.package_source_name,
    package_ecosystem: serviceDependency.package_ecosystem,
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

  const createNavigationParams = () => {
    const params = preserveParams(location.search);
    params.set("pteamId", row.pteam_id);
    params.set("serviceId", row.service_id);
    return params;
  };

  const handleTabChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleCVEClick = () => {
    if (vuln?.vuln_id) {
      const params = preserveParams(location.search);
      navigate(`/vulns/${vuln.vuln_id}?` + params.toString());
    }
  };

  const handleTeamClick = () => {
    if (row?.pteam_id) {
      const params = createNavigationParams();
      navigate("/pteam?" + params.toString());
    }
  };

  const handleServiceClick = () => {
    if (row?.pteam_id && row?.service_id) {
      const params = createNavigationParams();
      navigate("/?" + params.toString());
    }
  };

  const handlePackageClick = () => {
    if (row?.pteam_id && row?.service_id && serviceDependency?.package_id) {
      const params = createNavigationParams();
      navigate(`/packages/${serviceDependency.package_id}?` + params.toString());
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
            <Tab label="Insights" />
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
                <LinkIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Team
              </Typography>
              <Typography>{pteamName || "-"}</Typography>
              <IconButton size="small" onClick={handleTeamClick}>
                <LinkIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Service
              </Typography>
              <Typography>{serviceName || "-"}</Typography>
              <IconButton size="small" onClick={handleServiceClick}>
                <LinkIcon color="primary" fontSize="small" />
              </IconButton>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Typography variant="h6" sx={{ width: 170 }}>
                Package
              </Typography>
              <Typography>
                {currentPackage
                  ? `${currentPackage.package_name} : ${currentPackage.package_ecosystem}`
                  : "-"}
              </Typography>
              <IconButton size="small" onClick={handlePackageClick}>
                <LinkIcon color="primary" fontSize="small" />
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
                <TicketHandlingStatusSelector
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

        {/* insights */}
        <CustomTabPanel value={value} index={2}>
          <RiskAnalysis
            ticketId={row.ticket_id}
            serviceName={serviceName}
            ecosystem={serviceDependency.package_ecosystem}
            cveId={vuln?.cve_id || "No Known CVE"}
            cvss={Number.isFinite(vuln?.cvss_v3_score) ? vuln.cvss_v3_score.toFixed(1) : "N/A"}
          />
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
