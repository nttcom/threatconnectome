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
import { useState } from "react";

import { TabPanel } from "../../components/TabPanel.jsx";
import { UUIDTypography } from "../../components/UUIDTypography.jsx";
import {
  usePackageDependencies,
  usePackageService,
  usePackageVulnCounts,
} from "../../hooks/Package/useApiForPackage";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth.js";
import { usePageParams } from "../../hooks/usePageParams";
import { APIError } from "../../utils/APIError.js";
import { noPTeamMessage } from "../../utils/const.js";
import { a11yProps, errorToString } from "../../utils/func";

import { CodeBlock } from "./CodeBlock.jsx";
import { PackageReferences } from "./PackageReferences.jsx";
import { VulnerabilityTable } from "./VulnerabilityTable/VulnerabilityTable";

export function Package() {
  const { packageId, pteamId, serviceId } = usePageParams();
  const [tabValue, setTabValue] = useState(0);
  const [open, setOpen] = useState(false);
  const theme = useTheme();
  const isMdUp = useMediaQuery(theme.breakpoints.up("md"));
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const getVulnIdsReady = !skipByAuth && pteamId && serviceId && packageId;

  const {
    service,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = usePackageService(pteamId, serviceId);

  const {
    solvedVulnCount,
    unsolvedVulnCount,
    solvedError,
    unsolvedError,
    solvedLoading,
    unsolvedLoading,
  } = usePackageVulnCounts({ pteamId, serviceId, packageId, getVulnIdsReady });

  const {
    data: packageDependencies,
    error: packageDependenciesError,
    isLoading: packageDependenciesIsLoading,
  } = usePackageDependencies({ pteamId, serviceId, packageId });

  const handleTooltipOpen = () => {
    if (!isMdUp) setOpen(true);
  };
  const handleTooltipClose = () => {
    if (!isMdUp) setOpen(false);
  };

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!getVulnIdsReady) return <></>;
  if (!serviceId) return <>Service ID is required</>;

  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamIsLoading) return <>Now loading Team...</>;
  if (packageDependenciesError)
    throw new APIError(errorToString(packageDependenciesError), { api: "getDependencies" });
  if (packageDependenciesIsLoading) return <>Now loading packageDependencies...</>;
  if (solvedError)
    throw new APIError(errorToString(solvedError), {
      api: "getPTeamVulnIdsTiedToServicePackage (solved)",
    });
  if (solvedLoading) return <>Now loading solved vuln count...</>;
  if (unsolvedError)
    throw new APIError(errorToString(unsolvedError), {
      api: "getPTeamVulnIdsTiedToServicePackage (unsolved)",
    });
  if (unsolvedLoading) return <>Now loading unsolved vuln count...</>;

  if (!packageDependencies || packageDependencies.length === 0) {
    return <>No dependencies found for this package.</>;
  }

  const references = packageDependencies.map((dependency) => ({
    dependencyId: dependency.dependency_id,
    target: dependency.target,
    version: dependency.package_version,
    service: service.service_name,
    package_name: dependency.package_name,
    package_source_name: dependency.package_source_name,
    package_manager: dependency.package_manager,
    ecosystem: dependency.package_ecosystem,
  }));

  const firstPackageDependency = packageDependencies[0];

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
          <PackageReferences references={references} service={service} />
        </Box>
      </Box>
      <CodeBlock visible={visibleCodeBlock} />
      <Divider />
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="pteam_tagged_vuln_tabs">
            <Tab label={`UNSOLVED VULNS (${unsolvedVulnCount})`} {...a11yProps(0)} />
            <Tab label={`SOLVED VULNS (${solvedVulnCount})`} {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <VulnerabilityTable relatedTicketStatus="unsolved" />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <VulnerabilityTable relatedTicketStatus="solved" />
        </TabPanel>
      </Box>
    </>
  );
}
