import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Stack,
} from "@mui/material";
import { Layers as LayersIcon } from "@mui/icons-material";

import {
  formatDate,
  getDiffText,
  getProductCategorybyValue,
  getEolStatus,
} from "../../utils/eolUtils";
import { EolVersionForUi, StatusBadge } from "./EolParts";

export function EolTable({ filteredEolVersions }: { filteredEolVersions: EolVersionForUi[] }) {
  return (
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
          {filteredEolVersions.length > 0 ? (
            filteredEolVersions.map((eolVersion) => (
              <TableRow
                key={eolVersion.eol_version_id}
                hover
                sx={{
                  bgcolor: getEolStatus(eolVersion.eol_from) === "expired" ? "error.50" : undefined,
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
  );
}
