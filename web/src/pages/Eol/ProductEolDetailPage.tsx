import { useState } from "react";
import { useLocation, useParams, Link as RouterLink } from "react-router-dom";
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

// @ts-expect-error TS7016
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetEoLsQuery } from "../../services/tcApi";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import {
  formatDate,
  getDiffDays,
  getProductCategorybyValue,
  WARNING_THRESHOLD_DAYS,
} from "../../utils/eolUtils";
// @ts-expect-error TS7016
import { preserveParams } from "../../utils/urlUtils";

const getEolStatus = (eolDateStr: string | null | undefined) => {
  const diffDays = getDiffDays(eolDateStr);
  if (!diffDays) return "unknown";
  if (diffDays < 0) return "expired";
  if (diffDays <= WARNING_THRESHOLD_DAYS) return "warning";
  return "active";
};

export function ProductEolDetail() {
  const { productId } = useParams();
  const [showExpired, setShowExpired] = useState(false);

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: eolsData,
    error: eolsError,
    isLoading: eolsIsLoading,
  } = useGetEoLsQuery(undefined, { skip });

  const location = useLocation();
  const preservedParams = preserveParams(location.search);

  if (skip) return <>Now loading auth token...</>;
  if (eolsError)
    throw new APIError(errorToString(eolsError), {
      api: "getEoLs",
    });
  if (eolsIsLoading) return <>Now loading EoLs...</>;

  const product = eolsData?.products.find((product) => product.eol_product_id === productId);
  if (!product) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">No products found</Alert>
        <Box mt={2}>
          <Link component={RouterLink} to={`/supported-products?${preservedParams.toString()}`}>
            Back to the Supported Products List
          </Link>
        </Box>
      </Container>
    );
  }
  const filteredVersions =
    (showExpired
      ? product.eol_versions
      : product.eol_versions?.filter(
          (eol_version) => getEolStatus(eol_version.eol_from) !== "expired",
        )) ?? [];
  const sortedVersions = [...filteredVersions].sort(
    (a, b) => new Date(b.eol_from).getTime() - new Date(a.eol_from).getTime(),
  );

  const latestUpdateDate = sortedVersions
    .map((eol_version) => new Date(eol_version.updated_at))
    .reduce((latest, current) => (current > latest ? current : latest), new Date(0));
  const latestUpdate =
    latestUpdateDate > new Date(0) ? latestUpdateDate.toLocaleDateString() : "N/A";

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumb */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component={RouterLink}
          to={`/eol?${preservedParams.toString()}`}
          underline="hover"
          color="inherit"
        >
          EOL List
        </Link>
        <Link
          component={RouterLink}
          to={`/supported-products?${preservedParams.toString()}`}
          underline="hover"
          color="inherit"
        >
          Supported Products
        </Link>
        <Typography color="text.primary">{product.name}</Typography>
      </Breadcrumbs>
      {/* Header */}
      <Stack direction="row" spacing={2} alignItems="center" mb={1}>
        <Typography variant="h5" fontWeight="bold">
          {product.name}
        </Typography>
        <Chip label={getProductCategorybyValue(product.product_category)} size="small" />
      </Stack>
      <Typography variant="body2" color="text.secondary" mb={3}>
        {product.description}
      </Typography>
      {/* Last updated / Filter */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        spacing={2}
        mb={2}
      >
        <Typography variant="caption" color="text.secondary">
          Last Updated: {latestUpdate}
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={showExpired}
              onChange={(e) => setShowExpired(e.target.checked)}
              size="small"
            />
          }
          label={<Typography variant="body2">Show discontinued versions</Typography>}
        />
      </Stack>
      {/* Release/Cycle list table */}
      <Paper variant="outlined">
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: "grey.100" }}>
              <TableRow>
                <TableCell>Version</TableCell>
                <TableCell>EOL Date</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedVersions.map((versionData) => {
                const status = getEolStatus(versionData.eol_from);
                return (
                  <TableRow
                    key={versionData.eol_version_id}
                    sx={{
                      bgcolor: status === "expired" ? "error.50" : undefined,
                      opacity: status === "expired" ? 0.7 : 1,
                    }}
                  >
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography fontWeight={600}>{versionData.version}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>{formatDate(versionData.eol_from)}</TableCell>
                    <TableCell>
                      {status === "expired" && (
                        <Chip icon={<CancelIcon />} label="Ended" size="small" color="error" />
                      )}
                      {status === "warning" && (
                        <Chip
                          icon={<ScheduleIcon />}
                          label="Ending Soon"
                          size="small"
                          color="warning"
                        />
                      )}
                      {status === "active" && (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label="Supported"
                          size="small"
                          color="success"
                        />
                      )}
                      {status === "unknown" && (
                        <Chip label="Undecided" size="small" color="default" />
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
        {sortedVersions.length === 0 && (
          <Box p={4} textAlign="center">
            <Typography color="text.secondary">
              No versions to display. Please turn on “Show discontinued versions.”
            </Typography>
          </Box>
        )}
      </Paper>
      <Box mt={4}>
        <Link
          component={RouterLink}
          to={`/supported-products?${preservedParams.toString()}`}
          sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}
        >
          <ArrowBackIcon fontSize="small" />
          Back to the Supported Products List
        </Link>
      </Box>
    </Container>
  );
}
