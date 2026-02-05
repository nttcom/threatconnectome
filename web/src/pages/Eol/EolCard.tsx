import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";

import {
  formatDate,
  getDiffDays,
  getEolStatus,
  getProductCategorybyValue,
  getStatusLabel,
  Status,
} from "../../utils/eolUtils";

import { PTeamServiceResponse } from "../../../types/types.gen.ts";

// --- Status Settings ---
export const statusConfig = {
  expired: {
    color: "error",
    icon: <ErrorIcon />,
  },
  warning: {
    color: "warning",
    icon: <WarningIcon />,
  },
  active: {
    color: "success",
    icon: <CheckCircleIcon />,
  },
  unknown: {
    color: "default",
    icon: undefined,
  },
} as const;

const StatusBadge = ({ status }: { status: Status }) => {
  const config = statusConfig[status];
  return (
    <Chip icon={config.icon} label={getStatusLabel(status)} size="small" color={config.color} />
  );
};

const getDiffText = (eolDateStr: string) => {
  const diffDays = getDiffDays(eolDateStr);

  if (diffDays === null || diffDays === undefined) return "-";
  if (diffDays < 0) return `${Math.abs(diffDays)} days over`;
  if (diffDays === 0) return "Expires today";
  return `${diffDays} days left`;
};

type EolVersionForUi = {
  eol_version_id: string;
  eol_from: string;
  product_category: string;
  product_name: string;
  version: string;
  services: PTeamServiceResponse[];
};

export function EolCardList({ filteredEolVersions }: { filteredEolVersions: EolVersionForUi[] }) {
  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      {filteredEolVersions.map((eolVersion) => (
        <Card
          key={eolVersion.eol_version_id}
          variant="outlined"
          sx={{ bgcolor: getEolStatus(eolVersion.eol_from) === "expired" ? "error.50" : undefined }}
        >
          <CardContent>
            {/* ヘッダー：ステータスとカテゴリ */}
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

            {/* プロダクト名とバージョン */}
            <Typography sx={{ fontWeight: "bold", wordBreak: "break-word" }}>
              {eolVersion.product_name}{" "}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              v{eolVersion.version}
            </Typography>

            {/* EOL日と残り日数 */}
            <Typography variant="caption" color="text.secondary">
              EOL: {formatDate(eolVersion.eol_from) || "-"} ({getDiffText(eolVersion.eol_from)})
            </Typography>

            {/* サービス一覧 */}
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
