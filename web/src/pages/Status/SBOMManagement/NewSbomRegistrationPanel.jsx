/* eslint-disable react/prop-types */
import DescriptionIcon from "@mui/icons-material/Description";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { AppButton } from "./sharedUiParts";
import { slate } from "./styleTokens";

export function NewSbomRegistrationPanel({ onCancel, onUploadClick, showCancel = true }) {
  const { t } = useTranslation("status", { keyPrefix: "NewSbomRegistrationPanel" });
  return (
    <Box
      sx={{
        bgcolor: "white",
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        borderTopRightRadius: 24,
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
        p: { sm: 4, xs: 2 },
      }}
    >
      <Card
        sx={{
          border: `1px solid ${slate[200]}`,
          borderRadius: 6,
          boxShadow: "none",
          maxWidth: 768,
          mx: "auto",
          overflow: "hidden",
        }}
      >
        <Box sx={{ bgcolor: slate[50], px: { sm: 5, xs: 3 }, py: 5, textAlign: "center" }}>
          <Box
            sx={{
              alignItems: "center",
              bgcolor: "white",
              borderRadius: 6,
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
              display: "flex",
              height: 64,
              justifyContent: "center",
              mb: 2.5,
              mx: "auto",
              width: 64,
            }}
          >
            <DescriptionIcon sx={{ color: slate[500], fontSize: 32 }} />
          </Box>
          <Typography
            component="h2"
            sx={{ color: slate[950], fontSize: 24, fontWeight: 800, letterSpacing: 0 }}
          >
            {t("registerNewSbom")}
          </Typography>
          <Typography
            sx={{
              color: slate[600],
              fontSize: 14,
              lineHeight: "24px",
              maxWidth: 576,
              mt: 1.5,
              mx: "auto",
            }}
          >
            {t("registerNewSbomDesc")}
          </Typography>
        </Box>
        <CardContent sx={{ p: { sm: 4, xs: 3 } }}>
          <Stack sx={{ gap: 2.5 }}>
            <Box
              component="button"
              onClick={onUploadClick}
              sx={{
                "&:hover": { bgcolor: "white", borderColor: slate[400] },
                alignItems: "center",
                bgcolor: slate[50],
                border: `1px dashed ${slate[300]}`,
                borderRadius: 6,
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                font: "inherit",
                justifyContent: "center",
                px: 3,
                py: 5,
                textAlign: "center",
                transition: "background-color 160ms ease, border-color 160ms ease",
                width: "100%",
              }}
              type="button"
            >
              <UploadFileIcon sx={{ color: slate[400], fontSize: 32, mb: 1.5 }} />
              <Typography
                component="span"
                sx={{ color: slate[800], fontSize: 14, fontWeight: 700 }}
              >
                {t("uploadFirstSbom")}
              </Typography>
              <Typography component="span" sx={{ color: slate[500], fontSize: 12, mt: 0.5 }}>
                CycloneDX JSON / SPDX JSON
              </Typography>
            </Box>
            {showCancel && (
              <Box sx={{ display: "flex", justifyContent: "center" }}>
                <AppButton onClick={onCancel} variant="outlined">
                  {t("cancel")}
                </AppButton>
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
