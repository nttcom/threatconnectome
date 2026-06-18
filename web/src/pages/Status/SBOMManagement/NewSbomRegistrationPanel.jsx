/* eslint-disable react/prop-types */
import DescriptionIcon from "@mui/icons-material/Description";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { useSbomFileDrop } from "../SbomDrop/useSbomFileDrop";

import { AppButton } from "./sharedUiParts";
import {
  slate,
  statusCardSx,
  surfaceShadowSx,
  tabPanelSx,
  uiRadii,
  uiTransitions,
} from "./styleTokens";

export function NewSbomRegistrationPanel({
  onCancel,
  onDropFile,
  onUploadClick,
  showCancel = true,
}) {
  const { t } = useTranslation("status", { keyPrefix: "NewSbomRegistrationPanel" });
  const { t: tFileDropZone } = useTranslation("status", { keyPrefix: "FileDropZone" });

  const { isDragOver, handleDragEnter, handleDragOver, handleDragLeave, handleDrop } =
    useSbomFileDrop({
      onFile: (file) => onDropFile?.(file),
      onError: (key) => alert(tFileDropZone(key)),
    });

  return (
    <Box
      sx={{
        ...tabPanelSx,
        p: { sm: 4, xs: 2 },
      }}
    >
      <Card
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        sx={{
          ...statusCardSx,
          borderColor: isDragOver ? slate[400] : slate[200],
          maxWidth: 768,
          mx: "auto",
          overflow: "hidden",
          transition: uiTransitions.borderOnly,
        }}
      >
        <Box sx={{ bgcolor: slate[50], px: { sm: 5, xs: 3 }, py: 5, textAlign: "center" }}>
          <Box
            sx={{
              alignItems: "center",
              bgcolor: "white",
              borderRadius: uiRadii.statusCard,
              ...surfaceShadowSx,
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
                borderRadius: uiRadii.statusCard,
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                font: "inherit",
                justifyContent: "center",
                px: 3,
                py: 5,
                textAlign: "center",
                transition: uiTransitions.borderOnly,
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
