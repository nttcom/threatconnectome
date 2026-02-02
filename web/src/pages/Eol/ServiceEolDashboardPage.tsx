import { useState } from "react";
import { Link as RouterLink, useLocation } from "react-router-dom";
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
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Search as SearchIcon,
  Inventory2 as PackageIcon,
  Info as InfoIcon,
  Layers as LayersIcon,
} from "@mui/icons-material";

// @ts-expect-error TS7016
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import {
  formatDate,
  getDiffDays,
  getLatestUpdateDate,
  getProductCategorybyValue,
  getStatusLabel,
  getEolStatus,
} from "../../utils/eolUtils";
import type { Status } from "../../utils/eolUtils";
// @ts-expect-error TS7016
import { preserveParams } from "../../utils/urlUtils";
import { useGetPTeamEoLsQuery } from "../../services/tcApi";
import { EolCardList } from "./EolCard";

const getDiffText = (eolDateStr: string) => {
  const diffDays = getDiffDays(eolDateStr);

  if (diffDays === null || diffDays === undefined) return "-";
  if (diffDays < 0) return `${Math.abs(diffDays)} days over`;
  if (diffDays === 0) return "Expires today";
  return `${diffDays} days left`;
};

// --- Status Settings ---
const statusConfig = {
  expired: {
    color: "error",
    icon: <ErrorIcon fontSize="small" />,
  },
  warning: {
    color: "warning",
    icon: <WarningIcon fontSize="small" />,
  },
  active: {
    color: "success",
    icon: <CheckCircleIcon fontSize="small" />,
  },
  unknown: {
    color: "default",
    icon: undefined,
  },
} as const;

// --- Component ---
const StatusBadge = ({ status }: { status: Status }) => {
  const config = statusConfig[status];
  return (
    <Chip icon={config.icon} label={getStatusLabel(status)} size="small" color={config.color} />
  );
};

export function ServiceEolDashboard() {
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
  if (eolIsLoading) return <>Now loading Eol...</>;
  if (!eols) return <>Eol data not found</>;

  const filteredEoLProducts = eols.products.filter((eolProduct) => {
    return (eolProduct?.eol_versions ?? []).some((eolVersion) => {
      const status = getEolStatus(eolVersion.eol_from);
      const matchesFilter = filter === "all" || filter === status;
      const matchesSearch =
        eolProduct.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        eolVersion.services.some((s) =>
          s.service_name.toLowerCase().includes(searchTerm.toLowerCase()),
        );
      return matchesFilter && matchesSearch;
    });
  });

  const sortEolList = filteredEoLProducts
    .flatMap((eolProduct) =>
      (eolProduct.eol_versions ?? []).map((version) => ({
        ...version,
        product_name: eolProduct.name,
        product_category: eolProduct.product_category,
      })),
    )
    .sort((a, b) => {
      // Display expired items first, then by date (invalid dates at the bottom)
      const dateA = a.eol_from ? new Date(a.eol_from).getTime() : Infinity;
      const dateB = b.eol_from ? new Date(b.eol_from).getTime() : Infinity;
      const finalA = isNaN(dateA) ? Infinity : dateA;
      const finalB = isNaN(dateB) ? Infinity : dateB;

      return finalA - finalB;
    });

  const latestUpdate = getLatestUpdateDate(filteredEoLProducts);

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
            EOL List
          </Typography>
          <Typography variant="body2" color="text.secondary">
            List of EOL Status for Libraries and Tools Used by the Entire Team.
          </Typography>
        </Box>
      </Stack>

      {/* Info / Disclaimer Box */}
      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 4 }}>
        <AlertTitle>EOL Notification</AlertTitle>
        <Typography variant="body2" component="div">
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            <li>
              Supported tools will be automatically notified via Slack or email six months prior to
              their EOL date.
            </li>
            <li>
              Due to technical limitations, EOL information for all tools may not be accurately
              supported. Unsupported tools are not eligible for notifications. Please check the EOL
              information separately.
            </li>
            <li>
              Please check{" "}
              <Link component={RouterLink} to={`/supported-products?${preservedParams.toString()}`}>
                here
              </Link>{" "}
              for a list of supported tools.
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
        Last Updated: {latestUpdate}
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
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="expired">Expired</MenuItem>
                <MenuItem value="warning">Deadline approaching</MenuItem>
                <MenuItem value="active">Supported</MenuItem>
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
              <ToggleButton value="all">All</ToggleButton>
              <ToggleButton value="expired">Expired</ToggleButton>
              <ToggleButton value="warning">Deadline approaching</ToggleButton>
              <ToggleButton value="active">Supported</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <TextField
            placeholder="Search by product or service name..."
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
          // Mobile: Card View (mock data)
          <EolCardList />
        ) : (
          // Desktop: Table View
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: "grey.100" }}>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell>Product / Version</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>EOL date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredEoLProducts.length > 0 ? (
                  sortEolList.map((eolVersion) => (
                    <TableRow
                      key={eolVersion.eol_version_id}
                      hover
                      sx={{
                        bgcolor:
                          getEolStatus(eolVersion.eol_from) === "expired" ? "error.50" : undefined,
                      }}
                    >
                      <TableCell>
                        <StatusBadge status={getEolStatus(eolVersion.eol_from)} />
                        <Typography variant="caption" display="block" color="text.secondary">
                          {getDiffText(eolVersion.eol_from)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography fontWeight={600}>{eolVersion.product_name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          v{eolVersion.version}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                          {eolVersion.services.map((s) => (
                            <Chip
                              key={s.service_id}
                              label={s.service_name}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getProductCategorybyValue(eolVersion.product_category)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatDate(eolVersion.eol_from) || "-"}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                      <LayersIcon color="disabled" sx={{ fontSize: 48, mb: 1 }} />
                      <Typography color="text.secondary">No matching products found</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Box p={2} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="text.secondary">
            Total: {eols.total}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
