import UpdateIcon from "@mui/icons-material/Update";
import { Card, CardContent, Chip, Box, Typography, Stack } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useTranslation } from "react-i18next";
import { useNavigate, useLocation } from "react-router-dom";
import type { VulnResponse } from "../../../types/types.gen";

import { cvssProps, cvssConvertToName } from "../../utils/cvssUtils";
import { preserveParams } from "../../utils/urlUtils";

import { FormattedDateTimeWithTooltip } from "./FormattedDateTimeWithTooltip";

type VulnManagementCardListProps = {
  vulns: VulnResponse[];
};

export function VulnManagementCardList({ vulns }: VulnManagementCardListProps) {
  const { t } = useTranslation("vulnManagement", { keyPrefix: "VulnManagementCardList" });
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Stack spacing={2} sx={{ mt: 1 }}>
      {vulns?.length > 0 ? (
        vulns.map((vuln) => {
          const cvss = cvssConvertToName(vuln.cvss_v3_score ?? 0) as keyof typeof cvssProps;
          const cveId = vuln.cve_id == null ? t("noKnownCve") : vuln.cve_id;

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
        <Typography>{t("noVulns")}</Typography>
      )}
    </Stack>
  );
}
