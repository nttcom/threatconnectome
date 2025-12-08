import { Chip, TableCell, TableRow, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useLocation, useNavigate } from "react-router-dom";

import { cvssProps } from "../../utils/const";
import { cvssConvertToName } from "../../utils/func";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";

export function VulnManagementTableRow(props) {
  const { vuln } = props;

  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);

  const cvssScore =
    vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null ? "N/A" : vuln.cvss_v3_score;

  const cvss = cvssConvertToName(cvssScore);
  const cveId = vuln.cve_id === null ? "No Known CVE" : vuln.cve_id;

  return (
    <TableRow
      key={vuln.vuln_id}
      sx={{
        height: 80,
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
        borderLeft: `solid 5px ${cvssProps[cvss].cvssBgcolor}`,
      }}
      onClick={() => navigate(`/vulns/${vuln.vuln_id}?${params.toString()}`)}
    >
      <TableCell>
        <FormattedDateTimeWithTooltip utcString={vuln.updated_at} />
      </TableCell>
      <TableCell>
        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
          {vuln.title}
        </Typography>
      </TableCell>
      <TableCell>
        <Chip key={cveId} label={cveId} size="small" sx={{ m: 0.5, borderRadius: 0.5 }} />
      </TableCell>
    </TableRow>
  );
}
VulnManagementTableRow.propTypes = {
  vuln: PropTypes.object.isRequired,
};
