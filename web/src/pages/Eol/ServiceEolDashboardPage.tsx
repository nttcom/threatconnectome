import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link as RouterLink, useLocation } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
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
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Search as SearchIcon,
  Inventory2 as PackageIcon,
  Info as InfoIcon,
} from "@mui/icons-material";

// @ts-expect-error TS7016
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { getLatestUpdateDate, getEolStatus } from "../../utils/eolUtils";
// @ts-expect-error TS7016
import { preserveParams } from "../../utils/urlUtils";
import { useGetPTeamEoLsQuery } from "../../services/tcApi";

import { EolCardList } from "./EolCardList";
import { EolVersionForUi } from "./EolParts";
import { EolTable } from "./EolTable";

export function ServiceEolDashboard() {
  const { t } = useTranslation("eol", { keyPrefix: "ServiceEolDashboardPage" });
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const pteamId = params.get("pteamId");
  const preservedParams = preserveParams(location.search);

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: eols,
    error: eolError,
    isLoading: eolIsLoading,
  } = useGetPTeamEoLsQuery({ pteam_id: pteamId! }, { skip });

  if (skip) return <></>;
  if (eolError) throw new APIError(errorToString(eolError), { api: "getPTeamEoLs" });
  if (eolIsLoading) return <>{t("loadingEol")}</>;
  if (!eols) return <>{t("eolNotFound")}</>;

  const filteredEolVersions: EolVersionForUi[] = eols.products
    .flatMap((eolProduct) =>
      (eolProduct.eol_versions ?? []).map((version) => ({
        ...version,
        product_name: eolProduct.name,
        product_category: eolProduct.product_category,
      })),
    )
    .filter((eolVersion) => {
      const status = getEolStatus(eolVersion.eol_from);
      const matchesFilter = filter === "all" || filter === status;

      const matchesSearch =
        eolVersion.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        eolVersion.services.some((s) =>
          s.service_name.toLowerCase().includes(searchTerm.toLowerCase()),
        );

      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      // Display expired items first, then by date (invalid dates at the bottom)
      const dateA = a.eol_from ? new Date(a.eol_from).getTime() : Infinity;
      const dateB = b.eol_from ? new Date(b.eol_from).getTime() : Infinity;
      const finalA = isNaN(dateA) ? Infinity : dateA;
      const finalB = isNaN(dateB) ? Infinity : dateB;

      return finalA - finalB;
    });

  const latestUpdate = getLatestUpdateDate(filteredEolVersions);

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
            {t("title")}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t("subtitle")}
          </Typography>
        </Box>
      </Stack>

      {/* Info / Disclaimer Box */}
      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 4 }}>
        <AlertTitle>{t("notificationTitle")}</AlertTitle>
        <Typography variant="body2" component="div">
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            <li>{t("notificationItems.autoNotify")}</li>
            <li>{t("notificationItems.limitations")}</li>
            <li>
              {t("notificationItems.checkSupported")}{" "}
              <Link component={RouterLink} to={`/supported-products?${preservedParams.toString()}`}>
                {t("notificationItems.here")}
              </Link>{" "}
              {t("notificationItems.checkSupportedEnd")}
            </li>
          </Box>
        </Typography>
      </Alert>

      {/* EOL Last Updated */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: "block", textAlign: "right", mb: 1 }}
      >
        {t("lastUpdated")}: {latestUpdate}
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
            {/* Mobile: Select */}
            <FormControl size="small" sx={{ display: { xs: "block", md: "none" }, minWidth: 200 }}>
              <Select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <MenuItem value="all">{t("filterAll")}</MenuItem>
                <MenuItem value="expired">{t("filterExpired")}</MenuItem>
                <MenuItem value="warning">{t("filterWarning")}</MenuItem>
                <MenuItem value="active">{t("filterActive")}</MenuItem>
              </Select>
            </FormControl>
            {/* Desktop: ToggleButtonGroup */}
            <ToggleButtonGroup
              value={filter}
              exclusive
              onChange={handleFilterChange}
              size="small"
              sx={{ display: { xs: "none", md: "flex" } }}
            >
              <ToggleButton value="all">{t("filterAll")}</ToggleButton>
              <ToggleButton value="expired">{t("filterExpired")}</ToggleButton>
              <ToggleButton value="warning">{t("filterWarning")}</ToggleButton>
              <ToggleButton value="active">{t("filterActive")}</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <TextField
            placeholder={t("searchPlaceholder")}
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

        {/* Tools Table / Card View */}
        {isMdDown ? (
          // Mobile: Card View
          <EolCardList filteredEolVersions={filteredEolVersions} />
        ) : (
          // Desktop: Table View
          <EolTable filteredEolVersions={filteredEolVersions} />
        )}

        <Box p={2} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="text.secondary">
            {t("total")}: {filteredEolVersions.length}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
