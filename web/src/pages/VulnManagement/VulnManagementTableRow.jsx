import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  HorizontalRule as HorizontalRuleIcon,
} from "@mui/icons-material";
import { Chip, TableCell, TableRow, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnActionsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { cvssProps } from "../../utils/const";
import { errorToString, cvssConvertToName } from "../../utils/func";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";

export function VulnManagementTableRow(props) {
  const { vuln } = props;

  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);

  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: vulnActions,
    error: vulnActionsError,
    isLoading: vulnActionsIsLoading,
  } = useGetVulnActionsQuery(vuln.vuln_id, { skip });

  if (vulnActionsError)
    throw new APIError(errorToString(vulnActionsError), {
      api: "getVulnActions",
    });

  if (skip || vulnActionsIsLoading)
    return (
      <TableRow>
        <TableCell>Now loading vulnActions...</TableCell>
      </TableRow>
    );

  const cvssScore =
    vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null ? "N/A" : vuln.cvss_v3_score;

  const cvss = cvssConvertToName(cvssScore);

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
      <TableCell align="center">
        {vulnActions?.length > 0 ? (
          <CheckCircleOutlineIcon color="success" />
        ) : (
          <HorizontalRuleIcon sx={{ color: grey[500] }} />
        )}
      </TableCell>
      <TableCell>
        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
          {vuln.title}
        </Typography>
      </TableCell>
      <TableCell>
        <Chip
          key={vuln.cve_id}
          label={vuln.cve_id}
          size="small"
          sx={{ m: 0.5, borderRadius: 0.5 }}
        />
      </TableCell>
    </TableRow>
  );
}
VulnManagementTableRow.propTypes = {
  vuln: PropTypes.object.isRequired,
};
