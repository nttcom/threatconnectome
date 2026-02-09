import { Box, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

export function SmsTroubleshootingTips() {
  const { t } = useTranslation("components", { keyPrefix: "SmsTroubleshootingTips" });
  const resolvedTips = [t("tip1"), t("tip2"), t("tip3"), t("tip4")];

  return (
    <Box
      sx={{
        width: "100%",
        mt: 1,
        pl: 1,
      }}
    >
      <Typography variant="body2" sx={{ ml: 0.5, fontWeight: 600 }} gutterBottom>
        {t("title")}
      </Typography>
      <Box
        component="ol"
        sx={{
          pl: 4,
          m: 0,
          fontSize: (theme) => theme.typography.body2.fontSize,
        }}
      >
        {resolvedTips.map((tip) => (
          <Box
            component="li"
            key={tip}
            sx={{
              mb: 0.5,
            }}
          >
            {tip}
          </Box>
        ))}
      </Box>
    </Box>
  );
}
