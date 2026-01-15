import { useState, useMemo } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  Stack,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  Link,
  Alert,
  AlertTitle,
} from "@mui/material";
import {
  Search as SearchIcon,
  Inventory2 as PackageIcon,
  ArrowBack as ArrowBackIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import { SUPPORTED_PRODUCTS, DATA_LAST_UPDATED } from "./mocks/supportedProducts";
// --- 定数 ---
const PRODUCT_CATEGORIES = ["OS", "ランタイム", "ミドルウェア", "パッケージ"];

export function ProductEolList() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const navigate = useNavigate();
  const filteredProducts = useMemo(() => {
    return SUPPORTED_PRODUCTS.filter((product) => {
      const matchesSearch =
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === "all" || product.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, selectedCategory]);
  const latestUpdate = DATA_LAST_UPDATED;
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* ヘッダー */}
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <PackageIcon color="primary" fontSize="large" />
        <Box>
          <Typography variant="h5" fontWeight="bold">
            EOL情報自動取得対応製品一覧
          </Typography>
          <Typography variant="body2" color="text.secondary">
            EOL情報の自動取得・通知に対応している製品の一覧です
          </Typography>
        </Box>
      </Stack>
      {/* 注意文 */}
      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
        <AlertTitle>このページについて</AlertTitle>
        <Typography variant="body2">
          このページに掲載されている製品のみ、EOL日の自動取得・通知に対応しています。
          掲載されていない製品については、公式サイト等で別途EOL情報をご確認ください。
        </Typography>
      </Alert>
      {/* 更新日時 */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: "block", textAlign: "right", mb: 1 }}
      >
        データ最終更新日: {latestUpdate}
      </Typography>
      {/* 検索・フィルター */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems="center"
          justifyContent="space-between"
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              label="すべて"
              color={selectedCategory === "all" ? "primary" : "default"}
              onClick={() => setSelectedCategory("all")}
              variant={selectedCategory === "all" ? "filled" : "outlined"}
            />
            {PRODUCT_CATEGORIES.map((cat) => (
              <Chip
                key={cat}
                label={cat}
                color={selectedCategory === cat ? "primary" : "default"}
                onClick={() => setSelectedCategory(cat)}
                variant={selectedCategory === cat ? "filled" : "outlined"}
              />
            ))}
          </Stack>
          <TextField
            placeholder="製品名で検索..."
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ width: { xs: "100%", md: 300 } }}
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
      </Paper>
      {/* 製品カード一覧 */}
      <Grid container spacing={2}>
        {filteredProducts.map((product) => {
          return (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={product.id}>
              <Card variant="outlined">
                <CardActionArea onClick={() => navigate(`/supported-products/${product.id}`)}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Typography variant="h6" fontWeight="bold">
                        {product.name}
                      </Typography>
                      <Chip label={product.category} size="small" />
                    </Stack>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mt: 1, mb: 2, minHeight: 40 }}
                    >
                      {product.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      {filteredProducts.length === 0 && (
        <Paper variant="outlined" sx={{ p: 6, textAlign: "center" }}>
          <Typography color="text.secondary">該当する製品が見つかりません</Typography>
        </Paper>
      )}
      {/* メインページへのリンク */}
      <Box mt={4}>
        <Link
          component={RouterLink}
          to="/"
          sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}
        >
          <ArrowBackIcon fontSize="small" />
          EOL一覧に戻る
        </Link>
      </Box>
    </Container>
  );
}
