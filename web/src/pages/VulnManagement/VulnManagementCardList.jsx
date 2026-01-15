import UpdateIcon from "@mui/icons-material/Update";
import { Card, CardContent, Chip, Box, Typography, Stack } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useNavigate, useLocation } from "react-router-dom";

import { cvssProps, cvssConvertToName } from "../../utils/cvssUtils";
import { preserveParams } from "../../utils/urlUtils";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";

export function VulnManagementCardList({ vulns }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Stack spacing={2} sx={{ mt: 1 }}>
      {vulns?.length > 0 ? (
        vulns.map((vuln) => {
          const cvssScore =
            vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null
              ? "N/A"
              : vuln.cvss_v3_score;

          const cvss = cvssConvertToName(cvssScore);
          const cveId = vuln.cve_id === null ? "No Known CVE" : vuln.cve_id;

          const handleCardClick = () => {
            const preservedParams = preserveParams(location.search);
            navigate(`/vulns/${vuln.vuln_id}?` + preservedParams.toString());
          };

          return (
            <Card
              key={vuln.vuln_id}
              variant="outlined"
              sx={{
                borderLeft: `solid 5px ${cvssProps[cvss].cvssBgcolor}`,
                cursor: "pointer",
                "&:hover": { bgcolor: grey[100] },
              }}
              onClick={handleCardClick}
            >
              <CardContent>
                <Chip label={cveId} size="small" sx={{ borderRadius: 0.5, mr: 1 }} />
                <Typography
                  variant="subtitle1"
                  sx={{ overflowWrap: "anywhere", fontWeight: "bold" }}
                >
                  {vuln.title}
                </Typography>
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

VulnManagementCardList.propTypes = {
  vulns: PropTypes.array.isRequired,
};
