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
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { useState } from "react";

import VulnerabilityDialog from "./VulnerabilityDialog";

export default function PackagePage({ initialVulnerabilities = [], members = [] }) {
  const [vulnerabilities, setVulnerabilities] = useState(initialVulnerabilities);
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const handleRowClick = (vulnerability) => {
    setSelectedVuln(vulnerability);
  };

  const handleCloseDialog = () => {
    setSelectedVuln(null);
  };

  const handleSaveChanges = (updatedVulnerability) => {
    setVulnerabilities((currentVulnerabilities) =>
      currentVulnerabilities.map((vuln) =>
        vuln.id === updatedVulnerability.id ? updatedVulnerability : vuln,
      ),
    );
  };

  const theme = createTheme({
    shape: { borderRadius: 8 },
    palette: {
      primary: { main: "#1976d2" },
      warning: { main: "#f57c00" },
      success: { main: "#2e7d32" },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 3, bgcolor: "#f4f6f8", minHeight: "100vh" }}>
        <Typography variant="h4" sx={{ fontWeight: "bold", mb: 3 }}>
          Vulnerability Dashboard
        </Typography>
        <Paper elevation={0} sx={{ borderRadius: 4 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: "bold" }}>Title</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }} align="center">
                    Tasks
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
                      sx={{ cursor: "pointer" }}
                    >
                      <TableCell>{vuln.title}</TableCell>
                      <TableCell align="center">{vuln.tasks.length}</TableCell>
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

        <VulnerabilityDialog
          open={!!selectedVuln}
          onClose={handleCloseDialog}
          vulnerability={selectedVuln}
          members={members}
          onSave={handleSaveChanges}
        />
      </Box>
    </ThemeProvider>
  );
}
