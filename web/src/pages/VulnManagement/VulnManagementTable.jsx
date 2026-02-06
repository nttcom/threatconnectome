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
import { useTranslation } from "react-i18next";

import { VulnManagementTableRow } from "./VulnManagementTableRow";

export function VulnManagementTable(props) {
  const { t } = useTranslation("vulnManagement", { keyPrefix: "VulnManagementTable" });
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
                  {t("lastUpdate")}
                </Typography>
                <Tooltip title={t("timezoneTooltip")}>
                  <InfoIcon sx={{ color: grey[600], ml: 1 }} />
                </Tooltip>
              </Box>
            </TableCell>
            <TableCell style={{ width: "28%", fontWeight: 900 }}>{t("title")}</TableCell>
            <TableCell style={{ width: "35%", fontWeight: 900 }}>{t("cveId")}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {vulns?.length > 0 ? (
            vulns.map((vuln) => <VulnManagementTableRow key={vuln.vuln_id} vuln={vuln} />)
          ) : (
            <TableRow>
              <TableCell>{t("noVulns")}</TableCell>
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
