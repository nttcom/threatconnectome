import { useState } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Stack,
  Breadcrumbs,
  Link,
  FormControlLabel,
  Switch,
  Alert,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import { SUPPORTED_PRODUCTS, DATA_LAST_UPDATED } from "./mocks/supportedProducts";
const getEolStatus = (eolDateStr: string | null | undefined) => {
  if (!eolDateStr) return "unknown";
  const today = new Date();
  const eolDate = new Date(eolDateStr);
  const diffTime = eolDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return "expired";
  if (diffDays <= 180) return "warning";
  return "active";
};
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return "未定";
  return new Date(dateStr).toLocaleDateString("ja-JP");
};

export function ProductEolDetail() {
  const { productId } = useParams();
  const [showExpired, setShowExpired] = useState(false);
  const product = SUPPORTED_PRODUCTS.find((p) => p.id === productId);
  if (!product) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">製品が見つかりません</Alert>
        <Box mt={2}>
          <Link component={RouterLink} to="/supported-products">
            サポート対象製品一覧に戻る
          </Link>
        </Box>
      </Container>
    );
  }
  const filteredReleases = showExpired
    ? product.releases
    : product.releases.filter((r) => getEolStatus(r.eol) !== "expired");
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* パンくずリスト */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} to="/" underline="hover" color="inherit">
          EOL一覧
        </Link>
        <Link component={RouterLink} to="/supported-products" underline="hover" color="inherit">
          サポート対象製品
        </Link>
        <Typography color="text.primary">{product.name}</Typography>
      </Breadcrumbs>
      {/* ヘッダー */}
      <Stack direction="row" spacing={2} alignItems="center" mb={1}>
        <Typography variant="h5" fontWeight="bold">
          {product.name}
        </Typography>
        <Chip label={product.category} size="small" />
      </Stack>
      <Typography variant="body2" color="text.secondary" mb={3}>
        {product.description}
      </Typography>
      {/* 更新日時・フィルター */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        spacing={2}
        mb={2}
      >
        <Typography variant="caption" color="text.secondary">
          データ更新日: {DATA_LAST_UPDATED}
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={showExpired}
              onChange={(e) => setShowExpired(e.target.checked)}
              size="small"
            />
          }
          label={<Typography variant="body2">終了済みバージョンを表示</Typography>}
        />
      </Stack>
      {/* Release/Cycle一覧テーブル */}
      <Paper variant="outlined">
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: "grey.100" }}>
              <TableRow>
                <TableCell>バージョン</TableCell>
                <TableCell>リリース日</TableCell>
                <TableCell>EOL日</TableCell>
                <TableCell>ステータス</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredReleases.map((release) => {
                const status = getEolStatus(release.eol);
                return (
                  <TableRow
                    key={release.cycle}
                    sx={{
                      bgcolor: status === "expired" ? "error.50" : undefined,
                      opacity: status === "expired" ? 0.7 : 1,
                    }}
                  >
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography fontWeight={600}>{release.cycle}</Typography>
                        {release.lts && (
                          <Chip label="LTS" size="small" color="success" variant="outlined" />
                        )}
                      </Stack>
                    </TableCell>
                    <TableCell>{formatDate(release.releaseDate)}</TableCell>
                    <TableCell>
                      {release.eol ? (
                        formatDate(release.eol)
                      ) : (
                        <Typography variant="body2" color="text.secondary" fontStyle="italic">
                          未定
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {status === "expired" && (
                        <Chip icon={<CancelIcon />} label="終了" size="small" color="error" />
                      )}
                      {status === "warning" && (
                        <Chip
                          icon={<ScheduleIcon />}
                          label="終了間近"
                          size="small"
                          color="warning"
                        />
                      )}
                      {status === "active" && (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label="サポート中"
                          size="small"
                          color="success"
                        />
                      )}
                      {status === "unknown" && <Chip label="未定" size="small" color="default" />}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
        {filteredReleases.length === 0 && (
          <Box p={4} textAlign="center">
            <Typography color="text.secondary">
              表示するバージョンがありません。「終了済みバージョンを表示」をオンにしてください。
            </Typography>
          </Box>
        )}
      </Paper>
      {/* 戻るリンク */}
      <Box mt={4}>
        <Link
          component={RouterLink}
          to="/supported-products"
          sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}
        >
          <ArrowBackIcon fontSize="small" />
          サポート対象製品一覧に戻る
        </Link>
      </Box>
    </Container>
  );
}
