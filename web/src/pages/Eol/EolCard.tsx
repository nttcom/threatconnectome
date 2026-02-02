import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import { mockEolCardData, type Status } from "./mocks/eolCardData";
import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";

const statusConfig = {
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

const statusLabels = {
  expired: "Expired",
  warning: "Warning",
  active: "Active",
  unknown: "Unknown",
} as const;

const StatusBadge = ({ status }: { status: Status }) => {
  const config = statusConfig[status];
  return <Chip icon={config.icon} label={statusLabels[status]} color={config.color} size="small" />;
};

// モックデータを使用
export function EolCardList() {
  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      {mockEolCardData.map((item) => (
        <Card
          key={item.id}
          variant="outlined"
          sx={{ bgcolor: item.status === "expired" ? "error.50" : undefined }}
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
              <StatusBadge status={item.status} />
              <Chip label={item.category} size="small" />
            </Box>

            {/* プロダクト名とバージョン */}
            <Typography sx={{ fontWeight: "bold", wordBreak: "break-word" }}>
              {item.productName}{" "}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              v{item.version}
            </Typography>

            {/* EOL日と残り日数 */}
            <Typography variant="caption" color="text.secondary">
              EOL: {item.eolDate || "-"} ({item.diffText})
            </Typography>

            {/* サービス一覧 */}
            {item.services.length > 0 && (
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 1 }}>
                {item.services.map((service) => (
                  <Chip key={service.id} label={service.name} size="small" variant="outlined" />
                ))}
              </Stack>
            )}
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
