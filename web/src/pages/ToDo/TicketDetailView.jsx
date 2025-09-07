import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Box,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  IconButton,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { CustomTabPanel } from "../../components/CustomTabPanel.jsx";
import {
  useGetDependencyQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamServicesQuery,
  useGetVulnActionsQuery,
  useGetVulnQuery,
} from "../../services/tcApi";
import { ssvcPriorityProps } from "../../utils/const";
import { createActionByFixedVersions, findMatchedVulnPackage } from "../../utils/vulnUtils.js";
import { AssigneesSelector } from "../Package/VulnTables/AssigneesSelector.jsx";
import { SafetyImpactSelector } from "../Package/VulnTables/SafetyImpactSelector.jsx";
import { TicketHandlingStatusSelector } from "../Package/VulnTables/TicketHandlingStatusSelector.jsx";
import { VulnerabilityView } from "../Vulnerability/VulnerabilityView.jsx";

function DetailRow({ label, children }) {
  return (
    <Stack
      spacing={{ xs: 0.5, sm: 2 }}
      direction={{ xs: "column", sm: "row" }}
      sx={{ py: 1.5, alignItems: { sm: "flex-start", md: "center" } }}
    >
      <Typography
        variant="subtitle1"
        sx={{ width: { sm: 170 }, flexShrink: 0, fontWeight: "bold", color: "text.secondary" }}
      >
        {label}
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", flexWrap: "wrap", minWidth: 0 }}>
        {children}
      </Box>
    </Stack>
  );
}

export function TicketDetailView({ ticket }) {
  const [tabValue, setTabValue] = useState(0);

  const { data: pteam, isLoading: pteamIsLoading } = useGetPTeamQuery(ticket.pteam_id, {
    skip: !ticket.pteam_id,
  });
  const { data: service, isLoading: serviceIsLoading } = useGetPTeamServicesQuery(ticket.pteam_id, {
    selectFromResult: ({ data }) => ({
      data: data?.find((s) => s.service_id === ticket.service_id),
    }),
    skip: !ticket.pteam_id,
  });
  const { data: members, isLoading: membersIsLoading } = useGetPTeamMembersQuery(ticket.pteam_id, {
    skip: !ticket.pteam_id,
  });
  const { data: vuln, isLoading: vulnIsLoading } = useGetVulnQuery(ticket.vuln_id, {
    skip: !ticket.vuln_id,
  });
  const { data: vulnActions, isLoading: vulnActionsIsLoading } = useGetVulnActionsQuery(
    ticket.vuln_id,
    { skip: !ticket.vuln_id },
  );
  const { data: dependency, isLoading: dependencyIsLoading } = useGetDependencyQuery(
    { pteamId: ticket.pteam_id, dependencyId: ticket.dependency_id },
    { skip: !ticket.pteam_id || !ticket.dependency_id },
  );

  const isLoading =
    pteamIsLoading ||
    serviceIsLoading ||
    membersIsLoading ||
    vulnIsLoading ||
    vulnActionsIsLoading ||
    dependencyIsLoading;
  const ssvcPriority = ssvcPriorityProps[ticket.ssvc?.toLowerCase()] || ssvcPriorityProps["defer"];

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const currentPackage = {
    package_name: dependency?.package_name,
    package_source_name: dependency?.package_source_name,
    package_ecosystem: dependency?.package_ecosystem,
    vuln_matching_ecosystem: dependency?.vuln_matching_ecosystem,
  };

  const vulnerablePackage =
    findMatchedVulnPackage(vuln?.vulnerable_packages || [], currentPackage) || {};
  const actionByFixedVersions =
    createActionByFixedVersions(
      vulnerablePackage?.affected_versions ?? [],
      vulnerablePackage?.fixed_versions ?? [],
      vulnerablePackage?.affected_name,
    ) || {};

  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Ticket" />
          <Tab label="Vuln" />
        </Tabs>
      </Box>
      <CustomTabPanel value={tabValue} index={0}>
        <Stack divider={<Divider flexItem />}>
          <DetailRow label="SSVC">
            <Chip
              label={ticket.ssvc}
              sx={{ bgcolor: ssvcPriority?.style?.bgcolor, color: "#fff" }}
            />
          </DetailRow>
          <DetailRow label="CVE ID">
            <Typography>{vuln?.cve_id || ticket.cve}</Typography>
            <IconButton size="small">
              <OpenInNewIcon color="primary" fontSize="small" />
            </IconButton>
          </DetailRow>
          <DetailRow label="Team">
            <Typography>{pteam?.pteam_name}</Typography>
          </DetailRow>
          <DetailRow label="Service">
            <Typography>{service?.service_name}</Typography>
          </DetailRow>
          <DetailRow label="Package">
            <Typography sx={{ overflowWrap: "break-word" }}>{dependency?.package_name}</Typography>
          </DetailRow>
          <DetailRow label="Status">
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <TicketHandlingStatusSelector
                pteamId={ticket.pteam_id}
                serviceId={ticket.service_id}
                vulnId={ticket.vuln_id}
                packageId={dependency?.package_id}
                ticketId={ticket.ticket_id}
                currentStatus={ticket.ticket_status}
                actionByFixedVersions={actionByFixedVersions}
                vulnActions={vulnActions}
              />
            </FormControl>
          </DetailRow>
          <DetailRow label="Safety Impact">
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <SafetyImpactSelector pteamId={ticket.pteam_id} ticket={ticket} />
            </FormControl>
          </DetailRow>
          <DetailRow label="Assignees">
            <FormControl sx={{ width: 200 }} size="small" variant="standard">
              <AssigneesSelector
                pteamId={ticket.pteam_id}
                serviceId={ticket.service_id}
                vulnId={ticket.vuln_id}
                packageId={dependency?.package_id}
                ticketId={ticket.ticket_id}
                currentAssigneeIds={ticket.assignee}
                members={members}
              />
            </FormControl>
          </DetailRow>
        </Stack>
      </CustomTabPanel>
      <CustomTabPanel value={tabValue} index={1}>
        <VulnerabilityView vuln={vuln} vulnActions={vulnActions} currentPackage={currentPackage} />
      </CustomTabPanel>
    </>
  );
}

TicketDetailView.propTypes = {
  ticket: PropTypes.object.isRequired,
};
DetailRow.propTypes = {
  label: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};
CustomTabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};
