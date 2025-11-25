import { Typography, Box, Chip, Tabs, Tab, useMediaQuery, useTheme, Tooltip } from "@mui/material";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import { grey } from "@mui/material/colors";
import { useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import { UUIDTypography } from "../../../components/UUIDTypography";
import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
} from "../../../services/tcApi";
import { PackageReferences } from "../../Package/PackageReferences";
import VulnerabilitySplitDialog from "../VulnerabilitySplitDialog";

import VulnerabilityTable from "./VulnerabilityTable";

// import VulnerabilityDialog from "./VulnerabilityDialog";

// ------------------------------------------------------------------

export default function PackagePage({
  packageData = {},
  packageReferences = [],
  defaultSafetyImpact = "Not Set",
  ssvcCounts = {},
  initialVulnerabilities = [],
  members = [],
  serviceId = "service-id-from-props",
}) {
  const [vulnerabilities, setVulnerabilities] = useState(initialVulnerabilities);
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const handleRowClick = (vulnerability) => setSelectedVuln(vulnerability);
  const handleCloseDialog = () => setSelectedVuln(null);
  const handleSaveChanges = (updatedVulnerability) => {
    setVulnerabilities((current) =>
      current.map((v) => (v.id === updatedVulnerability.id ? updatedVulnerability : v)),
    );
  };
  const handleTabChange = (event, newValue) => setTabValue(newValue);

  const theme = useTheme();
  const isMdUp = useMediaQuery(theme.breakpoints.up("md"));

  const skipByAuth = useSkipUntilAuthUserIsReady();

  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const getPTeamReady = !skipByAuth && pteamId;
  const { packageId } = useParams();
  const getDependenciesReady = !skipByAuth && pteamId && serviceId;

  const offset = 0;
  const limit = 1000;
  const getVulnIdsReady = getPTeamReady && serviceId && packageId;

  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip: !getPTeamReady });
  const {
    data: serviceDependencies = [],
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    { pteamId, serviceId, packageId, offset, limit },
    { skip: !getDependenciesReady },
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
    data: vulnIdsSolved,
    error: vulnIdsSolvedError,
    isLoading: vulnIdsSolvedIsLoading,
  } = useGetPTeamVulnIdsTiedToServicePackageQuery(
    { pteamId, serviceId, packageId, relatedTicketStatus: "solved" },
    { skip: !getVulnIdsReady },
  );

  const serviceDict = pteam?.services?.find((service) => service.service_id === serviceId);
  const references =
    serviceDependencies?.map((dependency) => ({
      dependencyId: dependency.dependency_id,
      target: dependency.target,
      version: dependency.package_version,
      service: serviceDict?.service_name,
      package_name: dependency.package_name,
      package_source_name: dependency.package_source_name,
      package_manager: dependency.package_manager,
      ecosystem: dependency.package_ecosystem,
    })) || [];

  const [open, setOpen] = useState(false);
  const handleTooltipOpen = () => {
    if (!isMdUp) setOpen(true);
  };
  const handleTooltipClose = () => {
    if (!isMdUp) setOpen(false);
  };

  const firstPackageDependency = serviceDependencies?.[0] || packageData;

  const numUnsolved = vulnIdsUnSolved?.vuln_ids?.length ?? 0;
  const numSolved = vulnIdsSolved?.vuln_ids?.length ?? 0;

  return (
    <Box sx={{ p: 3 }}>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={2}>
        <Box display="flex" flexDirection="column" sx={{ width: "100%" }}>
          <Box>
            {isMdUp ? (
              <Tooltip title={serviceDict?.service_name}>
                <Chip
                  label={serviceDict?.service_name}
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
                  title={serviceDict?.service_name}
                >
                  <Chip
                    label={serviceDict?.service_name}
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
              {firstPackageDependency?.package_name || packageData.packageName || "Package"}
            </Typography>
            <Chip
              label={firstPackageDependency?.package_ecosystem || packageData.ecosystem || "N/A"}
              sx={{ ml: 1 }}
            />
          </Box>
          <UUIDTypography sx={{ mr: 2, mb: 1 }}>
            {packageId || packageData.packageUUID}
          </UUIDTypography>
          <PackageReferences
            references={references.length > 0 ? references : packageReferences}
            serviceDict={serviceDict}
          />
        </Box>
      </Box>

      {/* グローバルコントロール */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label={`Unsolved vulns (${numUnsolved || 0})`} />
          <Tab label={`Solved vulns (${numSolved || 0})`} />
        </Tabs>
      </Box>

      <VulnerabilityTable
        vulnerabilities={vulnerabilities}
        ssvcCounts={ssvcCounts}
        defaultSafetyImpact={defaultSafetyImpact}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={setPage}
        onRowsPerPageChange={(newRowsPerPage) => {
          setRowsPerPage(newRowsPerPage);
          setPage(0);
        }}
        onRowClick={handleRowClick}
      />

      {/* ダイアログ */}
      {/* {selectedVuln && (
        <VulnerabilityDialog
          open={!!selectedVuln}
          onClose={handleCloseDialog}
          vulnerability={selectedVuln}
          members={members}
          onSave={handleSaveChanges}
        />
      )} */}

      <VulnerabilitySplitDialog open={!!selectedVuln} onClose={handleCloseDialog} />
    </Box>
  );
}
