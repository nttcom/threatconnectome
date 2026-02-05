import { Box, Card, CardContent, Chip, Paper, Stack, Typography } from "@mui/material";
import { Layers as LayersIcon } from "@mui/icons-material";

import {
  formatDate,
  getEolStatus,
  getDiffText,
  getProductCategorybyValue,
} from "../../utils/eolUtils";
import { EolVersionForUi, StatusBadge } from "./EolParts";

export function EolCardList({ filteredEolVersions }: { filteredEolVersions: EolVersionForUi[] }) {
  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      {filteredEolVersions.length === 0 && (
        <Paper variant="outlined" sx={{ p: 6, textAlign: "center" }}>
          <LayersIcon color="disabled" sx={{ fontSize: 48, mb: 1 }} />
          <Typography color="text.secondary">No matching products found</Typography>
        </Paper>
      )}
      {filteredEolVersions.map((eolVersion) => (
        <Card
          key={eolVersion.eol_version_id}
          variant="outlined"
          sx={{ bgcolor: getEolStatus(eolVersion.eol_from) === "expired" ? "error.50" : undefined }}
        >
          <CardContent>
            {/* Header: Status and Category */}
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                mb: 1,
              }}
            >
              <StatusBadge status={getEolStatus(eolVersion.eol_from)} />
              <Chip label={getProductCategorybyValue(eolVersion.product_category)} size="small" />
            </Box>

            {/* Product Name and Version */}
            <Typography sx={{ fontWeight: "bold", wordBreak: "break-word" }}>
              {eolVersion.product_name}{" "}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              v{eolVersion.version}
            </Typography>

            {/* EOL Date and Remaining Days */}
            <Typography variant="caption" color="text.secondary">
              EOL: {formatDate(eolVersion.eol_from) || "-"} ({getDiffText(eolVersion.eol_from)})
            </Typography>

            {/* - List of Services */}
            {eolVersion.services.length > 0 && (
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 1 }}>
                {eolVersion.services.map((service) => (
                  <Chip
                    key={service.service_id}
                    label={service.service_name}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Stack>
            )}
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
