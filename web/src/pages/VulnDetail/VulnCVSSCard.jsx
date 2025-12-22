import { Avatar, Box, Card, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

import { cvssProps, cvssConvertToName } from "../../utils/cvssUtils";

export function VulnCVSSCard(props) {
  const { vuln } = props;
  const cvssScore =
    vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null ? "N/A" : vuln.cvss_v3_score;

  const cvss = cvssConvertToName(cvssScore);

  return (
    <Card variant="outlined" sx={{ margin: 1, backgroundColor: cvssProps[cvss].threatCardBgcolor }}>
      <Box sx={{ margin: 3 }}>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Avatar
            sx={{
              mr: 3,
              height: 60,
              width: 60,
              fontWeight: "bold",
              backgroundColor: cvssProps[cvss].cvssBgcolor,
            }}
            variant="rounded"
          >
            {cvssScore === "N/A" ? cvssScore : cvssScore.toFixed(1)}
          </Avatar>
          <Typography variant="h5">{vuln.title}</Typography>
        </Box>
        <Box sx={{ mt: 2, ml: 1 }}>
          <Typography sx={{ color: grey[700] }}>{vuln.detail}</Typography>
        </Box>
      </Box>
    </Card>
  );
}
VulnCVSSCard.propTypes = {
  vuln: PropTypes.object,
};
