import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
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
    <Box sx={{ p: 3, bgcolor: "#f4f6f8" }}>
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
      <Paper elevation={0} sx={{ borderRadius: 4 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell align="center">Tasks</TableCell>
                <TableCell align="center">Highest SSVC</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Affected Version</TableCell>
                <TableCell>Patched Version</TableCell>
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
                    sx={{ cursor: "pointer" }}
                  >
                    <TableCell>{vuln.title || "No Title"}</TableCell>
                    <TableCell align="center">{vuln.tasks?.length || 0}</TableCell>
                    <TableCell align="center">
                      <SSVCPriorityChip priority={vuln.highestSsvc} />
                    </TableCell>
                    <TableCell>{vuln.updated_at || "-"}</TableCell>
                    <TableCell>{(vuln.affected_versions || []).join("\n")}</TableCell>
                    <TableCell>{(vuln.patched_versions || []).join("\n")}</TableCell>
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
      </Paper>

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
