import { Info as InfoIcon } from "@mui/icons-material";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
  Paper,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

import { VulnManagementTableRow } from "./VulnManagementTableRow";

export function VulnManagementTable(props) {
  const { vulns } = props;

  return (
    <TableContainer
      component={Paper}
      sx={{
        mt: 1,
        border: `1px solid ${grey[300]}`,
        "&:before": { display: "none" },
      }}
    >
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell style={{ width: "20%" }}>
              <Box display="flex" flexDirection="row">
                <Typography variant="body2" sx={{ fontWeight: 900 }}>
                  Last Update
                </Typography>
                <Tooltip title="Timezone is local time">
                  <InfoIcon sx={{ color: grey[600], ml: 1 }} />
                </Tooltip>
              </Box>
            </TableCell>
            <TableCell style={{ width: "28%", fontWeight: 900 }}>Title</TableCell>
            <TableCell style={{ width: "35%", fontWeight: 900 }}>CVE ID</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {vulns?.length > 0 ? (
            vulns.map((vuln) => <VulnManagementTableRow key={vuln.vuln_id} vuln={vuln} />)
          ) : (
            <TableRow>
              <TableCell>No vulns</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
VulnManagementTable.propTypes = {
  vulns: PropTypes.array.isRequired,
};
