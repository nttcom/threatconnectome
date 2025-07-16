import UpdateIcon from "@mui/icons-material/Update";
import { Card, CardContent, Chip, Box, Typography, Stack } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

import { cvssProps } from "../../utils/const";
import { cvssConvertToName } from "../../utils/func";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";

export function VulnManagementCardList({ vulns }) {
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

VulnManagementCardList.propTypes = {
  vulns: PropTypes.array.isRequired,
};
