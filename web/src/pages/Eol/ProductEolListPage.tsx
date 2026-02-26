import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate, Link as RouterLink } from "react-router-dom";
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

// @ts-expect-error TS7016
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetEoLsQuery } from "../../services/tcApi";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import {
  getEoLProductCategoryList,
  getLatestUpdateDate,
  getProductCategorybyValue,
} from "../../utils/eolUtils";
// @ts-expect-error TS7016
import { preserveParams } from "../../utils/urlUtils";

export function ProductEolList() {
  const { t } = useTranslation("eol", { keyPrefix: "ProductEolListPage" });
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: eolsData,
    error: eolsError,
    isLoading: eolsIsLoading,
  } = useGetEoLsQuery(undefined, { skip });

  const navigate = useNavigate();
  const location = useLocation();
  const preservedParams = preserveParams(location.search);
  const filteredProducts = useMemo(() => {
    return (
      eolsData?.products.filter((eolProduct) => {
        const matchesSearch = eolProduct.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory =
          selectedCategory === "all" || eolProduct.product_category === selectedCategory;
        return matchesSearch && matchesCategory;
      }) ?? []
    );
  }, [eolsData, searchTerm, selectedCategory]);

  const latestUpdate = getLatestUpdateDate(filteredProducts.flatMap((p) => p.eol_versions ?? []));

  if (skip) return <>{t("loadingAuth")}</>;
  if (eolsError)
    throw new APIError(errorToString(eolsError), {
      api: "getEoLs",
    });
  if (eolsIsLoading) return <>{t("loadingEols")}</>;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <PackageIcon color="primary" fontSize="large" />
        <Box>
          <Typography variant="h5" fontWeight="bold">
            {t("title")}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t("subtitle")}
          </Typography>
        </Box>
      </Stack>
      {/* Notice */}
      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
        <AlertTitle>{t("aboutPageTitle")}</AlertTitle>
        <Typography variant="body2">{t("aboutPageContent")}</Typography>
      </Alert>
      {/* Last Updated */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: "block", textAlign: "right", mb: 1 }}
      >
        {t("lastUpdated")}: {latestUpdate}
      </Typography>
      {/* Search and Filter */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems="center"
          justifyContent="space-between"
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              label={t("filterAll")}
              color={selectedCategory === "all" ? "primary" : "default"}
              onClick={() => setSelectedCategory("all")}
              variant={selectedCategory === "all" ? "filled" : "outlined"}
            />
            {getEoLProductCategoryList().map((category) => (
              <Chip
                key={category.value}
                label={category.label}
                color={selectedCategory === category.value ? "primary" : "default"}
                onClick={() => setSelectedCategory(category.value)}
                variant={selectedCategory === category.value ? "filled" : "outlined"}
              />
            ))}
          </Stack>
          <TextField
            placeholder={t("searchPlaceholder")}
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
      {/* Product Card List */}
      <Grid container spacing={2}>
        {filteredProducts.map((product) => (
          <Grid
            size={{ xs: 12, sm: 6, md: 4 }}
            key={product.eol_product_id}
            sx={{ display: "flex" }}
          >
            <Card
              variant="outlined"
              sx={{ width: "100%", height: "100%", display: "flex", flexDirection: "column" }}
            >
              <CardActionArea
                onClick={() =>
                  navigate(
                    `/supported-products/${product.eol_product_id}?` + preservedParams.toString(),
                  )
                }
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Typography variant="h6" fontWeight="bold">
                      {product.name}
                    </Typography>
                    <Chip
                      label={getProductCategorybyValue(product.product_category)}
                      size="small"
                    />
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
        ))}
      </Grid>
      {filteredProducts.length === 0 && (
        <Paper variant="outlined" sx={{ p: 6, textAlign: "center" }}>
          <Typography color="text.secondary">{t("noMatchingProducts")}</Typography>
        </Paper>
      )}
      {/* Link to Main Page */}
      <Box mt={4}>
        <Link
          component={RouterLink}
          to={`/eol?${preservedParams.toString()}`}
          sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}
        >
          <ArrowBackIcon fontSize="small" />
          {t("backToEolList")}
        </Link>
      </Box>
    </Container>
  );
}
