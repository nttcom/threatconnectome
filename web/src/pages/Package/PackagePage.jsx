import {
  Box,
  Divider,
  Tab,
  Tabs,
  Typography,
  Chip,
  Tooltip,
  ClickAwayListener,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useState } from "react";
import { useParams, useLocation } from "react-router-dom";

import { TabPanel } from "../../components/TabPanel.jsx";
import { UUIDTypography } from "../../components/UUIDTypography.jsx";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth.js";
import {
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetDependenciesQuery,
} from "../../services/tcApi.js";
import { APIError } from "../../utils/APIError.js";
import { noPTeamMessage } from "../../utils/const.js";
import { a11yProps, errorToString } from "../../utils/func.js";

import { CodeBlock } from "./CodeBlock.jsx";
import { PTeamVulnsPerPackage } from "./PTeamVulnsPerPackage.jsx";
import { PackageReferences } from "./PackageReferences.jsx";
import { VulnerabilityTable } from "./VulnerabilityTable/VulnerabilityTable.jsx";

export function Package({ useSplitView = false }) {
  const [tabValue, setTabValue] = useState(0);

  const skipByAuth = useSkipUntilAuthUserIsReady();

  const { packageId } = useParams();
  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");
  const getDependenciesReady = !skipByAuth && pteamId && serviceId;
  const getPTeamReady = !skipByAuth && pteamId;
  const getVulnIdsReady = getPTeamReady && serviceId && packageId;

  const offset = 0;
  const limit = 1000;
  const {
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    { pteamId, serviceId, packageId, offset, limit },
    { skip: !getDependenciesReady },
  );
  const {
    service,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, {
    skip: !getPTeamReady,
    selectFromResult: ({ data, error, isLoading }) => ({
      service: data?.services?.find((service) => service.service_id === serviceId),
      error,
      isLoading,
    }),
  });
  
  // Only fetch these when not using split view
  const {
    vulnIds: vulnIdsSolved,
    error: vulnIdsSolvedError,
    isLoading: vulnIdsSolvedIsLoading,
  } = useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    {
      skip: !getVulnIdsReady,
      selectFromResult: ({ data, error, isLoading }) => ({
        vulnIds: data?.vuln_ids,
        error,
        isLoading,
      }),
    },
  );
  const {
    vulnIds: vulnIdsUnSolved,
    error: vulnIdsUnSolvedError,
    isLoading: vulnIdsUnSolvedIsLoading,
  } = useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "unsolved" },
    {
      skip: !getVulnIdsReady,
      selectFromResult: ({ data, error, isLoading }) => ({
        vulnIds: data?.vuln_ids,
        error,
        isLoading,
      }),
    },
  );
  
  // Only fetch ticket counts when not using split view
  const {
    data: ticketCountsSolved,
    error: ticketCountsSolvedError,
    isLoading: ticketCountsSolvedIsLoading,
  } = useGetPTeamTicketCountsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    { skip: !getVulnIdsReady || useSplitView },
  );
  const {
    data: ticketCountsUnSolved,
    error: ticketCountsUnSolvedError,
    isLoading: ticketCountsUnSolvedIsLoading,
  } = useGetPTeamTicketCountsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "unsolved" },
    { skip: !getVulnIdsReady || useSplitView },
  );

  const [open, setOpen] = useState(false);

  const theme = useTheme();
  const isMdUp = useMediaQuery(theme.breakpoints.up("md"));

  const handleTooltipOpen = () => {
    if (!isMdUp) setOpen(true);
  };
  const handleTooltipClose = () => {
    if (!isMdUp) setOpen(false);
  };

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!getVulnIdsReady) return <></>;
  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamIsLoading) return <>Now loading Team...</>;
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getDependencies" });
  if (serviceDependenciesIsLoading) return <>Now loading serviceDependencies...</>;
  
  // Check vulnIds errors (needed for tab counts)
  if (vulnIdsSolvedError)
    throw new APIError(errorToString(vulnIdsSolvedError), {
      api: "getPTeamVulnIdsTiedToServicePackage",
    });
  if (vulnIdsSolvedIsLoading) return <>Now loading vulnIdsSolved...</>;
  if (vulnIdsUnSolvedError)
    throw new APIError(errorToString(vulnIdsUnSolvedError), {
      api: "getPTeamVulnIdsTiedToServicePackage",
    });
  if (vulnIdsUnSolvedIsLoading) return <>Now loading vulnIdsUnSolved...</>;
  
  // Only check ticket count errors when not using split view
  if (!useSplitView) {
    if (ticketCountsSolvedError)
      throw new APIError(errorToString(ticketCountsSolvedError), {
        api: "getPTeamTicketCountsTiedToServicePackage",
      });
    if (ticketCountsSolvedIsLoading) return <>Now loading ticketCountsSolved...</>;
    if (ticketCountsUnSolvedError)
      throw new APIError(errorToString(ticketCountsUnSolvedError), {
        api: "getPTeamTicketCountsTiedToServicePackage",
      });
    if (ticketCountsUnSolvedIsLoading) return <>Now loading ticketCountsUnSolved...</>;
  }

  const references = serviceDependencies.map((dependency) => ({
    dependencyId: dependency.dependency_id,
    target: dependency.target,
    version: dependency.package_version,
    service: service.service_name,
    package_name: dependency.package_name,
    package_source_name: dependency.package_source_name,
    package_manager: dependency.package_manager,
    ecosystem: dependency.package_ecosystem,
  }));

  if (!serviceDependencies || serviceDependencies.length === 0) {
    return <>No dependencies found for this package.</>;
  }

  const firstPackageDependency = serviceDependencies[0];

  const numSolved = vulnIdsSolved?.length ?? 0;
  const numUnsolved = vulnIdsUnSolved?.length ?? 0;

  const handleTabChange = (event, value) => setTabValue(value);

  // CodeBlock is not implemented
  const visibleCodeBlock = false;

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={2}>
        <Box display="flex" flexDirection="column" sx={{ width: "100%" }}>
          <Box>
            {isMdUp ? (
              <Tooltip title={service.service_name}>
                <Chip
                  label={service.service_name}
                  variant="outlined"
                  sx={{
                    borderRadius: "2px",
                    border: `1px solid ${grey[700]}`,
                    borderLeft: `5px solid ${grey[700]}`,
                    mr: 1,
                    mb: 1,
                  }}
                />
              </Tooltip>
            ) : (
              <ClickAwayListener onClickAway={handleTooltipClose}>
                <Tooltip
                  onClose={handleTooltipClose}
                  open={open}
                  disableFocusListener
                  disableHoverListener
                  disableTouchListener
                  title={service.service_name}
                >
                  <Chip
                    label={service.service_name}
                    variant="outlined"
                    sx={{
                      borderRadius: "2px",
                      border: `1px solid ${grey[700]}`,
                      borderLeft: `5px solid ${grey[700]}`,
                      mr: 1,
                      mb: 1,
                    }}
                    onClick={handleTooltipOpen}
                  />
                </Tooltip>
              </ClickAwayListener>
            )}
          </Box>
          <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="h4" sx={{ fontWeight: 900 }}>
              {firstPackageDependency.package_name}
            </Typography>
            <Chip label={firstPackageDependency.package_ecosystem} sx={{ ml: 1 }} />
          </Box>
          <Typography mr={1} mb={1} variant="caption">
            <UUIDTypography sx={{ mr: 2 }}>{packageId}</UUIDTypography>
          </Typography>
          <PackageReferences references={references} serviceDict={service} />
        </Box>
      </Box>
      <CodeBlock visible={visibleCodeBlock} />
      <Divider />
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="pteam_tagged_vuln_tabs">
            <Tab label={`UNSOLVED VULNS (${numUnsolved})`} {...a11yProps(0)} />
            <Tab label={`SOLVED VULNS (${numSolved})`} {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          {useSplitView ? (
            <VulnerabilityTable relatedTicketStatus="unsolved" />
          ) : (
            <PTeamVulnsPerPackage
              pteamId={pteamId}
              service={service}
              packageId={packageId}
              references={references}
              vulnIds={vulnIdsUnSolved}
              ticketCounts={ticketCountsUnSolved.ssvc_priority_count}
            />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          {useSplitView ? (
            <VulnerabilityTable relatedTicketStatus="solved" />
          ) : (
            <PTeamVulnsPerPackage
              pteamId={pteamId}
              service={service}
              packageId={packageId}
              references={references}
              vulnIds={vulnIdsSolved}
              ticketCounts={ticketCountsSolved.ssvc_priority_count}
            />
          )}
        </TabPanel>
      </Box>
    </>
  );
}

Package.propTypes = {
  useSplitView: PropTypes.bool,
};
