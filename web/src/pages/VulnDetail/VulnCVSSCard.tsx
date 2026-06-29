import { Avatar, Box, Card, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";

import type { VulnResponse } from "../../../types/types.gen";
import { cvssProps, cvssConvertToName } from "../../utils/cvssUtils";

type CVSSName = keyof typeof cvssProps;

type VulnCVSSCardProps = {
  vuln: VulnResponse;
};

export function VulnCVSSCard(props: VulnCVSSCardProps) {
  const { vuln } = props;
  const cvssScore =
    vuln.cvss_v3_score === undefined || vuln.cvss_v3_score === null ? null : vuln.cvss_v3_score;

  const cvss = (cvssScore === null ? "None" : cvssConvertToName(cvssScore)) as CVSSName;
  const displayCvssScore = cvssScore === null ? "N/A" : cvssScore.toFixed(1);

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
            {displayCvssScore}
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
