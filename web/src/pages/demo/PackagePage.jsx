import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
  Paper,
} from "@mui/material";
import { useState } from "react";

import VulnerabilitySplitDialog from "./VulnerabilitySplitDialog";

// import VulnerabilityDialog from "./VulnerabilityDialog";

// --- ヘルパーコンポーネント (変更なし) ---

function SSVCPriorityChip({ priority, count }) {
  const styles = {
    immediate: { bgcolor: "#d32f2f", color: "white" },
    high: { bgcolor: "#f57c00", color: "white" },
    medium: { bgcolor: "#fbc02d", color: "black" },
    low: { bgcolor: "#388e3c", color: "white" },
    none: { bgcolor: "#e0e0e0", color: "black" },
  };
  const label = count !== undefined ? `${priority}: ${count}` : priority || "none";
  return <Chip label={label} size="small" sx={styles[priority] || styles.none} />;
}

function UUIDTypography({ children }) {
  return (
    <Typography sx={{ fontFamily: "monospace", color: "text.secondary" }}>{children}</Typography>
  );
}

function PackageReferences({ references = [] }) {
  if (!references.length) return null;
  return (
    <Accordion
      disableGutters
      elevation={0}
      sx={{
        mt: 2,
        bgcolor: "background.paper",
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        "&:before": { display: "none" },
      }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="body2">Show/Hide References</Typography>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 0 }}>
        <TableContainer sx={{ maxHeight: 200 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Target</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Service</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {references.map((ref, index) => (
                <TableRow key={`${ref.target}-${index}`}>
                  <TableCell>{ref.target}</TableCell>
                  <TableCell>{ref.version}</TableCell>
                  <TableCell>{ref.service}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </AccordionDetails>
    </Accordion>
  );
}

// ------------------------------------------------------------------

export default function PackagePage({
  packageData = {},
  packageReferences = [],
  defaultSafetyImpact = "Not Set", // defaultSafetyImpactをpropsで受け取る
  ssvcCounts = {},
  tabCounts = {},
  initialVulnerabilities = [],
  members = [],
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

  return (
    <Box sx={{ p: 3 }}>
      {/* ページヘッダー */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
          <Chip label={packageData.serviceName || "Service"} size="small" />
          <Typography variant="h4" component="h1" sx={{ fontWeight: "bold" }}>
            {packageData.packageName || "Package"}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Chip label={packageData.packageManager || "Manager"} variant="outlined" size="small" />
          <UUIDTypography>{packageData.packageUUID || "UUID"}</UUIDTypography>
        </Box>
        <PackageReferences references={packageReferences} />
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
          <Tab label={`Unsolved (${tabCounts.unsolved || 0})`} />
          <Tab label={`Solved (${tabCounts.solved || 0})`} />
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
