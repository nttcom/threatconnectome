import { Info as InfoIcon } from "@mui/icons-material";
import UpdateIcon from "@mui/icons-material/Update";
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
  Card,
  CardContent,
  Chip,
  useTheme,
  useMediaQuery,
  Stack,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

import { cvssProps } from "../../utils/const";
import { cvssConvertToName } from "../../utils/func";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";
import { VulnManagementTableRow } from "./VulnManagementTableRow";

export function VulnManagementTable(props) {
  const { vulns } = props;
  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  if (isMdDown) {
    return (
      <Stack spacing={2} sx={{ mt: 1 }}>
        {vulns?.length > 0 ? (
          vulns.map((vuln) => {
            const cvssScore =
              vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null
                ? "N/A"
                : vuln.cvss_v3_score;

            const cvss = cvssConvertToName(cvssScore);
            return (
              <Card
                key={vuln.vuln_id}
                variant="outlined"
                sx={{
                  borderLeft: `solid 5px ${cvssProps[cvss].cvssBgcolor}`,
                  cursor: "pointer",
                  "&:hover": { bgcolor: grey[100] },
                }}
                onClick={() => window.location.assign(`/vulns/${vuln.vuln_id}`)}
              >
                <CardContent>
                  <Chip
                    label={vuln.cve_id === null ? "No Known CVE" : vuln.cve_id}
                    size="small"
                    sx={{ borderRadius: 0.5 }}
                  />
                  <Box display="flex" alignItems="center" mb={1}>
                    <Typography
                      variant="subtitle1"
                      sx={{ overflowWrap: "anywhere", fontWeight: "bold" }}
                    >
                      {vuln.title}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <UpdateIcon sx={{ mr: 1 }} />
                    <FormattedDateTimeWithTooltip utcString={vuln.updated_at} />
                  </Box>
                </CardContent>
              </Card>
            );
          })
        ) : (
          <Typography>No vulns</Typography>
        )}
      </Stack>
    );
  }

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
            <TableCell style={{ width: "3%", fontWeight: 900 }}>Action</TableCell>
            <TableCell style={{ width: "25%", fontWeight: 900 }}>Title</TableCell>
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
