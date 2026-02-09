import LinkIcon from "@mui/icons-material/Link";
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
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { CustomTabPanel } from "../../components/CustomTabPanel.jsx";
import { AssigneesSelector } from "../../components/Ticket/AssigneesSelector";
import {
  useGetDependencyQuery,
  useGetPTeamQuery,
  useGetPTeamServicesQuery,
  useGetVulnQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError.js";
import { errorToString, utcStringToLocalDate } from "../../utils/func";
import { ssvcPriorityProps } from "../../utils/ssvcUtils";
import { preserveParams } from "../../utils/urlUtils.js";
import { RiskAnalysis } from "../ToDo/Insights/RiskAnalysis.jsx";

import { SafetyImpactSelector } from "./SafetyImpactSelector.jsx";
import { TicketHandlingStatusSelector } from "./TicketHandlingStatusSelector.jsx";
import { VulnerabilityView } from "./VulnerabilityView.jsx";

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
  const { t } = useTranslation("toDo", { keyPrefix: "TicketDetailView" });
  const [tabValue, setTabValue] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();

  const {
    data: pteam,
    isLoading: pteamIsLoading,
    error: pteamError,
  } = useGetPTeamQuery(
    { path: { pteam_id: ticket.pteam_id } },
    {
      skip: !ticket.pteam_id,
    },
  );

  const {
    data: service,
    isLoading: serviceIsLoading,
    error: pteamServicesError,
  } = useGetPTeamServicesQuery(
    { path: { pteam_id: ticket.pteam_id } },
    {
      selectFromResult: ({ data, isLoading, error }) => ({
        data: data?.find((s) => s.service_id === ticket.service_id),
        isLoading,
        error,
      }),
      skip: !ticket.pteam_id,
    },
  );

  const {
    data: vuln,
    isLoading: vulnIsLoading,
    error: vulnError,
  } = useGetVulnQuery(
    { path: { vuln_id: ticket.vuln_id } },
    {
      skip: !ticket.vuln_id,
    },
  );

  const {
    data: dependency,
    isLoading: dependencyIsLoading,
    error: dependencyError,
  } = useGetDependencyQuery(
    { path: { pteam_id: ticket.pteam_id, dependency_id: ticket.dependency_id } },
    { skip: !ticket.pteam_id || !ticket.dependency_id },
  );

  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamServicesError)
    throw new APIError(errorToString(pteamServicesError), { api: "getPTeamServices" });
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (dependencyError) throw new APIError(errorToString(dependencyError), { api: "getDependency" });

  const isLoading = pteamIsLoading || serviceIsLoading || vulnIsLoading || dependencyIsLoading;

  const ssvc = ticket.ssvc_deployer_priority;
  const ssvcPriority = ssvcPriorityProps[ssvc?.toLowerCase()] || ssvcPriorityProps["defer"];

  const dueDate = useMemo(() => {
    if (!ticket.ticket_status?.scheduled_at) return "-";
    const formattedDate = utcStringToLocalDate(ticket.ticket_status.scheduled_at, false);
    return formattedDate || "-";
  }, [ticket.ticket_status?.scheduled_at]);

  const createNavigationParams = () => {
    const params = preserveParams(location.search);
    params.set("pteamId", ticket.pteam_id);
    params.set("serviceId", ticket.service_id);
    return params;
  };
  const handleCVEClick = () => {
    if (vuln?.vuln_id) {
      navigate(`/vulns/${vuln.vuln_id}?` + preserveParams(location.search).toString());
    }
  };
  const handleTeamClick = () => {
    if (ticket?.pteam_id) navigate("/pteam?" + createNavigationParams().toString());
  };
  const handleServiceClick = () => {
    if (ticket?.pteam_id && ticket?.service_id)
      navigate("/?" + createNavigationParams().toString());
  };
  const handlePackageClick = () => {
    if (ticket?.pteam_id && ticket?.service_id && dependency?.package_id) {
      navigate(`/packages/${dependency.package_id}?` + createNavigationParams().toString());
    }
  };

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

  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label={t("tabTicket")} />
          <Tab label={t("tabVuln")} />
          <Tab label={t("tabInsights")} />
        </Tabs>
      </Box>
      <CustomTabPanel value={tabValue} index={0}>
        <Stack divider={<Divider flexItem />}>
          <DetailRow label={t("ssvc")}>
            <Chip
              label={ssvc || "-"}
              sx={{ bgcolor: ssvcPriority?.style?.bgcolor, color: "#fff" }}
            />
          </DetailRow>
          <DetailRow label={t("cveId")}>
            {vuln?.cve_id === null ? (
              <Typography>{t("noKnownCve")}</Typography>
            ) : (
              <Typography>{vuln?.cve_id || "-"}</Typography>
            )}
            <IconButton size="small" onClick={handleCVEClick}>
              <LinkIcon color="primary" fontSize="small" />
            </IconButton>
          </DetailRow>
          <DetailRow label={t("team")}>
            <Typography>{pteam?.pteam_name || "-"}</Typography>
            <IconButton size="small" onClick={handleTeamClick}>
              <LinkIcon color="primary" fontSize="small" />
            </IconButton>
          </DetailRow>
          <DetailRow label={t("service")}>
            <Typography>{service?.service_name || "-"}</Typography>
            <IconButton size="small" onClick={handleServiceClick}>
              <LinkIcon color="primary" fontSize="small" />
            </IconButton>
          </DetailRow>
          <DetailRow label={t("package")}>
            <Typography sx={{ overflowWrap: "break-word" }}>
              {dependency
                ? `${dependency.package_name || "-"} : ${dependency.package_ecosystem || "-"}`
                : "-"}
            </Typography>
            <IconButton size="small" onClick={handlePackageClick}>
              <LinkIcon color="primary" fontSize="small" />
            </IconButton>
          </DetailRow>
          <DetailRow label={t("target")}>
            <Typography>{dependency?.target || "-"}</Typography>
          </DetailRow>
          <DetailRow label={t("dueDate")}>
            <Typography>{dueDate}</Typography>
          </DetailRow>
          <DetailRow label={t("status")}>
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <TicketHandlingStatusSelector
                pteamId={ticket.pteam_id}
                serviceId={ticket.service_id}
                vulnId={ticket.vuln_id}
                packageId={dependency?.package_id}
                ticketId={ticket.ticket_id}
                currentStatus={ticket.ticket_status}
              />
            </FormControl>
          </DetailRow>
          <DetailRow label={t("safetyImpact")}>
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <SafetyImpactSelector
                pteamId={ticket.pteam_id}
                ticket={{
                  ticket_id: ticket.ticket_id,
                  ticket_safety_impact: ticket.ticket_safety_impact || null,
                  ticket_safety_impact_change_reason:
                    ticket.ticket_safety_impact_change_reason || null,
                }}
              />
            </FormControl>
          </DetailRow>
          <DetailRow label={t("assignees")}>
            <FormControl sx={{ width: 200 }} size="small" variant="standard">
              <AssigneesSelector
                ticketId={ticket.ticket_id}
                currentAssigneeIds={ticket.ticket_status?.assignees || []}
              />
            </FormControl>
          </DetailRow>
        </Stack>
      </CustomTabPanel>
      <CustomTabPanel value={tabValue} index={1}>
        <VulnerabilityView vuln={vuln} currentPackage={currentPackage} />
      </CustomTabPanel>
      <CustomTabPanel value={tabValue} index={2}>
        <RiskAnalysis
          ticketId={ticket.ticket_id}
          serviceName={service?.service_name || "-"}
          ecosystem={dependency?.package_ecosystem || "-"}
          cveId={vuln?.cve_id || "No Known CVE"}
          cvss={Number.isFinite(vuln?.cvss_v3_score) ? vuln.cvss_v3_score.toFixed(1) : "N/A"}
        />
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
