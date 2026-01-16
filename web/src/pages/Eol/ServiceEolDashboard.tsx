import { useState } from "react";
import { Link as RouterLink } from "react-router-dom";
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
  TextField,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  AlertTitle,
  Link,
  Stack,
  Select,
  MenuItem,
  FormControl,
} from "@mui/material";
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Search as SearchIcon,
  Inventory2 as PackageIcon,
  AllInclusive as InfinityIcon,
  Info as InfoIcon,
  Layers as LayersIcon,
  HelpOutline as HelpOutlineIcon,
} from "@mui/icons-material";

// --- 型定義 ---
type Status = "expired" | "warning" | "safe" | "continuous" | "unsupported";

type Dependency = {
  id: number;
  name: string;
  version: string;
  category: string;
  eol: string;
  isSupported: boolean;
  note: string;
};

type Service = {
  id: string;
  name: string;
  dependencies: Dependency[];
};

// --- ヘルパー関数 ---
const getStatus = (eolDateStr: string, isSupported: boolean = true): Status => {
  // サポート外の場合
  if (!isSupported) return "unsupported";

  // EOL日付がない場合は継続サポート
  if (!eolDateStr) return "continuous";

  const today = new Date();
  const eolDate = new Date(eolDateStr);
  const diffTime = eolDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return "expired";
  if (diffDays <= 180) return "warning";
  return "safe";
};

const getStatusLabel = (status: Status) => {
  switch (status) {
    case "expired":
      return "期限切れ";
    case "warning":
      return "期限間近";
    case "safe":
      return "サポート中";
    case "continuous":
      return "期限なし";
    case "unsupported":
      return "サポート外";
    default:
      return "";
  }
};

const getDiffText = (eolDateStr: string, isSupported: boolean = true) => {
  if (!isSupported) return "通知対象外";
  if (!eolDateStr) return "-";
  const today = new Date();
  const eolDate = new Date(eolDateStr);
  const diffTime = eolDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return `${Math.abs(diffDays)}日 超過`;
  if (diffDays === 0) return "今日終了";
  return `あと ${diffDays}日`;
};

// --- ステータス設定 ---
const statusConfig = {
  expired: {
    color: "error",
    icon: <ErrorIcon fontSize="small" />,
  },
  warning: {
    color: "warning",
    icon: <WarningIcon fontSize="small" />,
  },
  safe: {
    color: "success",
    icon: <CheckCircleIcon fontSize="small" />,
  },
  continuous: {
    color: "info",
    icon: <InfinityIcon fontSize="small" />,
  },
  unsupported: {
    color: "default",
    icon: <HelpOutlineIcon fontSize="small" />,
  },
} as const;

// --- コンポーネント ---
const StatusBadge = ({ status }: { status: Status }) => {
  const config = statusConfig[status];
  return (
    <Chip icon={config.icon} label={getStatusLabel(status)} size="small" color={config.color} />
  );
};

export function ServiceEolDashboard({
  services,
  lastUpdated,
}: {
  services: Service[];
  lastUpdated: string;
}) {
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  // 依存関係をグルーピング（名前とバージョンが同じものをまとめる）
  const groupedDependencies = (() => {
    const grouped: Record<string, Dependency & { services: { id: string; name: string }[] }> = {};

    services.forEach((service) => {
      service.dependencies.forEach((dep) => {
        const key = `${dep.name}-${dep.version}`;
        if (!grouped[key]) {
          grouped[key] = {
            ...dep,
            services: [{ id: service.id, name: service.name }],
          };
        } else {
          grouped[key].services.push({ id: service.id, name: service.name });
        }
      });
    });

    return Object.values(grouped);
  })();

  const filteredDependencies = groupedDependencies
    .filter((dep) => {
      const status = getStatus(dep.eol, dep.isSupported);
      // 「サポート中」フィルターには「期限なし」も含める
      const matchesFilter =
        filter === "all" || status === filter || (filter === "safe" && status === "continuous");
      const matchesSearch =
        dep.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        dep.services.some((s) => s.name.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      // 期限切れを優先表示、次に日付順（不正な日付は一番下）
      if (!a.eol && !b.eol) return 0;
      if (!a.eol) return 1;
      if (!b.eol) return -1;
      const dateA = new Date(a.eol).getTime();
      const dateB = new Date(b.eol).getTime();
      if (isNaN(dateA) && isNaN(dateB)) return 0;
      if (isNaN(dateA)) return 1;
      if (isNaN(dateB)) return -1;
      return dateA - dateB;
    });

  const handleFilterChange = (_event: React.MouseEvent<HTMLElement>, newFilter: string | null) => {
    if (newFilter !== null) {
      setFilter(newFilter);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <PackageIcon color="primary" fontSize="large" />
        <Box>
          <Typography variant="h5" fontWeight="bold">
            EOL 一覧
          </Typography>
          <Typography variant="body2" color="text.secondary">
            チーム全体で使用されているライブラリ・ツールのEOL状況リスト
          </Typography>
        </Box>
      </Stack>

      {/* Info / Disclaimer Box */}
      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 4 }}>
        <AlertTitle>EOL通知について</AlertTitle>
        <Typography variant="body2" component="div">
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            <li>サポート対象のツールは、EOL日の6ヶ月前にSlackまたはメールで自動通知されます。</li>
            <li>
              技術的な制約により、すべてのツールのEOL情報が正確にサポートされるわけではありません。サポート外のツールは通知対象外となりますので、別途EOL情報をご確認ください。
            </li>
            <li>
              サポート対象ツールの一覧は
              <Link component={RouterLink} to="/supported-products">
                こちら
              </Link>
              をご確認ください。
            </li>
          </Box>
        </Typography>
      </Alert>

      {/* EOL情報更新日 */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: "block", textAlign: "right", mb: 1 }}
      >
        EOL情報更新日: {lastUpdated}
      </Typography>

      {/* Filter & Search Controls */}
      <Paper variant="outlined" sx={{ mb: 3 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          justifyContent="space-between"
          alignItems="center"
          spacing={2}
          p={2}
        >
          <Box sx={{ width: { xs: "100%", md: "auto" } }}>
            {/* モバイル: Select */}
            <FormControl size="small" sx={{ display: { xs: "block", md: "none" }, minWidth: 200 }}>
              <Select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <MenuItem value="all">すべて</MenuItem>
                <MenuItem value="expired">期限切れ</MenuItem>
                <MenuItem value="warning">期限間近</MenuItem>
                <MenuItem value="safe">サポート中</MenuItem>
                <MenuItem value="unsupported">サポート外</MenuItem>
              </Select>
            </FormControl>
            {/* デスクトップ: ToggleButtonGroup */}
            <ToggleButtonGroup
              value={filter}
              exclusive
              onChange={handleFilterChange}
              size="small"
              sx={{ display: { xs: "none", md: "flex" } }}
            >
              <ToggleButton value="all">すべて</ToggleButton>
              <ToggleButton value="expired">期限切れ</ToggleButton>
              <ToggleButton value="warning">期限間近</ToggleButton>
              <ToggleButton value="safe">サポート中</ToggleButton>
              <ToggleButton value="unsupported">サポート外</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <TextField
            placeholder="依存関係名またはサービス名で検索..."
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ width: { xs: "100%", md: 320 } }}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              },
            }}
          />
        </Stack>

        {/* Tools Table */}
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: "grey.100" }}>
              <TableRow>
                <TableCell>ステータス</TableCell>
                <TableCell>依存関係 / バージョン</TableCell>
                <TableCell>使用サービス</TableCell>
                <TableCell>カテゴリ</TableCell>
                <TableCell>EOL日付</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDependencies.length > 0 ? (
                filteredDependencies.map((dep, index) => (
                  <TableRow
                    key={`${dep.name}-${dep.version}-${index}`}
                    hover
                    sx={{
                      bgcolor:
                        getStatus(dep.eol, dep.isSupported) === "expired" ? "error.50" : undefined,
                    }}
                  >
                    <TableCell>
                      <StatusBadge status={getStatus(dep.eol, dep.isSupported)} />
                      <Typography variant="caption" display="block" color="text.secondary">
                        {getDiffText(dep.eol, dep.isSupported)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography fontWeight={600}>{dep.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        v{dep.version}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        {dep.services.map((s) => (
                          <Chip key={s.id} label={s.name} size="small" variant="outlined" />
                        ))}
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Chip label={dep.category} size="small" />
                    </TableCell>
                    <TableCell>{dep.eol || "-"}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                    <LayersIcon color="disabled" sx={{ fontSize: 48, mb: 1 }} />
                    <Typography color="text.secondary">該当する依存関係が見つかりません</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box p={2} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="text.secondary">
            表示件数: {filteredDependencies.length} 件
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
