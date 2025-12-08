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
import React, { useState } from "react";
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
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
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
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip: !getPTeamReady });
  const {
    data: vulnIdsSolved,
    error: vulnIdsSolvedError,
    isLoading: vulnIdsSolvedIsLoading,
  } = useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    { skip: !getVulnIdsReady },
  );
  const {
    data: vulnIdsUnSolved,
    error: vulnIdsUnSolvedError,
    isLoading: vulnIdsUnSolvedIsLoading,
  } = useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "unsolved" },
    { skip: !getVulnIdsReady },
  );
  const {
    data: ticketCountsSolved,
    error: ticketCountsSolvedError,
    isLoading: ticketCountsSolvedIsLoading,
  } = useGetPTeamTicketCountsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    { skip: !getVulnIdsReady },
  );
  const {
    data: ticketCountsUnSolved,
    error: ticketCountsUnSolvedError,
    isLoading: ticketCountsUnSolvedIsLoading,
  } = useGetPTeamTicketCountsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "unsolved" },
    { skip: !getVulnIdsReady },
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

  const serviceDict = pteam.services.find((service) => service.service_id === serviceId);
  const references = serviceDependencies.map((dependency) => ({
    dependencyId: dependency.dependency_id,
    target: dependency.target,
    version: dependency.package_version,
    service: serviceDict.service_name,
    package_name: dependency.package_name,
    package_source_name: dependency.package_source_name,
    package_manager: dependency.package_manager,
    ecosystem: dependency.package_ecosystem,
  }));

  if (!serviceDependencies || serviceDependencies.length === 0) {
    return <>No dependencies found for this package.</>;
  }

  const firstPackageDependency = serviceDependencies[0];

  const numSolved = vulnIdsSolved.vuln_ids?.length ?? 0;
  const numUnsolved = vulnIdsUnSolved.vuln_ids?.length ?? 0;

  const handleTabChange = (event, value) => setTabValue(value);

  // CodeBlock is not implemented
  const visibleCodeBlock = false;

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={2}>
        <Box display="flex" flexDirection="column" sx={{ width: "100%" }}>
          <Box>
            {isMdUp ? (
              <Tooltip title={serviceDict.service_name}>
                <Chip
                  label={serviceDict.service_name}
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
                  title={serviceDict.service_name}
                >
                  <Chip
                    label={serviceDict.service_name}
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
          <PackageReferences references={references} serviceDict={serviceDict} />
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
            <VulnerabilityTable
              vulnIds={vulnIdsUnSolved?.vuln_ids || []}
              defaultSafetyImpact={serviceDict?.service_safety_impact || "Not Set"}
              page={page}
              rowsPerPage={rowsPerPage}
              ticketCounts={ticketCountsUnSolved?.ssvc_priority_count || {}}
              onPageChange={setPage}
              onRowsPerPageChange={(newRowsPerPage) => {
                setRowsPerPage(newRowsPerPage);
                setPage(0);
              }}
            />
          ) : (
            <PTeamVulnsPerPackage
              pteamId={pteamId}
              service={serviceDict}
              packageId={packageId}
              references={references}
              vulnIds={vulnIdsUnSolved.vuln_ids}
              ticketCounts={ticketCountsUnSolved.ssvc_priority_count}
            />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          {useSplitView ? (
            <VulnerabilityTable
              vulnIds={vulnIdsSolved?.vuln_ids || []}
              defaultSafetyImpact={serviceDict?.service_safety_impact || "Not Set"}
              page={page}
              rowsPerPage={rowsPerPage}
              ticketCounts={ticketCountsSolved?.ssvc_priority_count || {}}
              onPageChange={setPage}
              onRowsPerPageChange={(newRowsPerPage) => {
                setRowsPerPage(newRowsPerPage);
                setPage(0);
              }}
            />
          ) : (
            <PTeamVulnsPerPackage
              pteamId={pteamId}
              service={serviceDict}
              packageId={packageId}
              references={references}
              vulnIds={vulnIdsSolved.vuln_ids}
              ticketCounts={ticketCountsSolved.ssvc_priority_count}
            />
          )}
        </TabPanel>
      </Box>
    </>
  );
}
