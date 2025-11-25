import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  TablePagination,
  Chip,
  Tabs,
  Tab,
  Stack,
  Paper,
  useMediaQuery,
  useTheme,
  Tooltip,
} from "@mui/material";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import { grey } from "@mui/material/colors";
import { useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import { UUIDTypography } from "../../components/UUIDTypography";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetDependenciesQuery,
  useGetPTeamQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
} from "../../services/tcApi";
import { PackageReferences } from "../Package/PackageReferences";

import VulnerabilitySplitDialog from "./VulnerabilitySplitDialog";

// import VulnerabilityDialog from "./VulnerabilityDialog";

function SSVCPriorityChip({ priority, count }) {
  const styles = {
    immediate: { bgcolor: "#d32f2f", color: "white" },
    "out-of-cycle": { bgcolor: "#f57c00", color: "white" },
    scheduled: { bgcolor: "#fbc02d", color: "black" },
    defer: { bgcolor: "#9e9e9e", color: "white" },
    none: { bgcolor: "#e0e0e0", color: "black" },
  };
  const label = count !== undefined ? `${priority}: ${count}` : priority || "none";
  return <Chip label={label} size="small" sx={styles[priority] || styles.none} />;
}

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

      <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
        {Object.entries(ssvcCounts).map(([priority, count]) => (
          <SSVCPriorityChip key={priority} priority={priority} count={count} />
        ))}
      </Stack>

      {/* === デフォルトSafety Impactの表示を追加 === */}
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, mb: 2 }}>
        Default Safety Impact: <strong>{defaultSafetyImpact}</strong>
      </Typography>

      {/* 脆弱性テーブル */}

      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead
            sx={{
              display: { xs: "none", sm: "table-header-group" },
            }}
          >
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell align="center" sx={{ display: { xs: "none", sm: "table-cell" } }}>
                Tasks
              </TableCell>
              <TableCell align="center">Highest SSVC</TableCell>
              <TableCell sx={{ display: { xs: "none", sm: "none", md: "table-cell" } }}>
                Last Updated
              </TableCell>
              <TableCell sx={{ display: { xs: "none", sm: "none", md: "none", lg: "table-cell" } }}>
                Affected Version
              </TableCell>
              <TableCell sx={{ display: { xs: "none", sm: "none", md: "none", lg: "table-cell" } }}>
                Patched Version
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {vulnerabilities
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((vuln) => (
                <TableRow
                  key={vuln.id}
                  onClick={() => handleRowClick(vuln)}
                  hover
                  sx={(theme) => ({
                    // theme を引数に取る
                    cursor: "pointer",
                    display: { xs: "block", sm: "table-row" },
                    // xs: カード型の時の下線 (カード間の境界)
                    borderBottom: { xs: `1px solid ${theme.palette.divider}`, sm: "none" },
                    padding: { xs: "16px", sm: 0 },
                    "&:last-of-type": {
                      borderBottom: { xs: "none" }, // 最後のカードの下線は消す
                    },

                    // ▼▼▼ 修正点 ▼▼▼
                    // sm以上の時、すべての子(TableCell)に強制的に下線を引く
                    "& > .MuiTableCell-root": {
                      borderBottom: { sm: `1px solid ${theme.palette.divider}` },
                    },
                    // ▲▲▲ 修正点 ▲▲▲
                  })}
                >
                  {/* Title */}
                  <TableCell
                    sx={{
                      display: { xs: "block", sm: "table-cell" },
                      padding: { xs: 0, sm: "16px" },
                      // xsの時は borderBottom を 'none' に (親の指定を上書き)
                      borderBottom: { xs: "none" },
                      marginBottom: { xs: "12px", sm: 0 },
                    }}
                  >
                    <Box
                      component="span"
                      sx={{
                        display: { xs: "block", sm: "none" },
                        fontWeight: "bold",
                        fontSize: "0.75rem",
                        color: "text.secondary",
                        marginBottom: "2px",
                      }}
                    >
                      Title
                    </Box>
                    {vuln.title || "No Title"}
                  </TableCell>

                  {/* Tasks (sm以上で表示) */}
                  <TableCell
                    align="center"
                    sx={{
                      display: { xs: "none", sm: "table-cell" },
                      // borderBottomの指定は不要 (親のTableRowが設定してくれる)
                    }}
                  >
                    {vuln.tasks?.length || 0}
                  </TableCell>

                  {/* Highest SSVC */}
                  <TableCell
                    align="center"
                    sx={{
                      display: { xs: "block", sm: "table-cell" },
                      padding: { xs: 0, sm: "16px" },
                      // xsの時は borderBottom を 'none' に (親の指定を上書き)
                      borderBottom: { xs: "none" },
                      textAlign: { xs: "left", sm: "center" },
                    }}
                  >
                    <Box
                      component="span"
                      sx={{
                        display: { xs: "block", sm: "none" },
                        fontWeight: "bold",
                        fontSize: "0.75rem",
                        color: "text.secondary",
                        marginBottom: "4px",
                      }}
                    >
                      Highest SSVC
                    </Box>
                    <SSVCPriorityChip priority={vuln.highestSsvc} />
                  </TableCell>

                  {/* Last Updated (md以上で表示) */}
                  <TableCell
                    sx={{
                      display: { xs: "none", sm: "none", md: "table-cell" },
                      // borderBottomの指定は不要 (親のTableRowが設定してくれる)
                    }}
                  >
                    {vuln.updated_at || "-"}
                  </TableCell>

                  {/* Affected Version (lg以上で表示) */}
                  <TableCell
                    sx={{
                      display: { xs: "none", sm: "none", md: "none", lg: "table-cell" },
                      // borderBottomの指定は不要 (親のTableRowが設定してくれる)
                    }}
                  >
                    {(vuln.affected_versions || []).join("\n")}
                  </TableCell>

                  {/* Patched Version (lg以上で表示) */}
                  <TableCell
                    sx={{
                      display: { xs: "none", sm: "none", md: "none", lg: "table-cell" },
                      // borderBottomの指定は不要 (親のTableRowが設定してくれる)
                    }}
                  >
                    {(vuln.patched_versions || []).join("\n")}
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={vulnerabilities.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
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
