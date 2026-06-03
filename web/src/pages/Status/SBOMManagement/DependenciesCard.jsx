/* eslint-disable react/prop-types */
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DescriptionIcon from "@mui/icons-material/Description";
import SearchIcon from "@mui/icons-material/Search";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Card, CardContent, Chip, MenuItem, Select, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip";

import { AppButton } from "./sharedUiParts";
import { compactSelectSx, slate } from "./styleTokens";

function DependencyTable({ dependencies, onPackageClick, pageStartIndex }) {
  const { t } = useTranslation("status", { keyPrefix: "DependenciesCard" });
  if (dependencies.length === 0) {
    return (
      <Box sx={{ p: 5, textAlign: "center" }}>
        <DescriptionIcon sx={{ color: slate[300], fontSize: 36, mb: 1.5 }} />
        <Typography sx={{ color: slate[600], fontSize: 14, fontWeight: 600 }}>
          {t("noDependencies")}
        </Typography>
        <Typography sx={{ color: slate[400], fontSize: 12, mt: 0.5 }}>
          {t("noDependenciesHelp")}
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {dependencies.map((dependency, index) => {
        const canNavigate = Boolean(onPackageClick && dependency.packageId && dependency.serviceId);
        const handleNavigate = () => {
          if (!canNavigate) {
            return;
          }
          onPackageClick(dependency.serviceId, dependency.packageId);
        };

        return (
          <Box
            key={`${dependency.name}-${dependency.version}-${pageStartIndex + index}`}
            onClick={handleNavigate}
            onKeyDown={(event) => {
              if (canNavigate && (event.key === "Enter" || event.key === " ")) {
                event.preventDefault();
                handleNavigate();
              }
            }}
            role={canNavigate ? "button" : undefined}
            tabIndex={canNavigate ? 0 : undefined}
            sx={{
              "&:hover": { bgcolor: slate[50] },
              alignItems: "center",
              borderTop: index === 0 ? 0 : `1px solid ${slate[100]}`,
              cursor: canNavigate ? "pointer" : "default",
              display: "grid",
              fontSize: 14,
              gridTemplateColumns: "48px 1.4fr 0.7fr 0.65fr 0.8fr",
              px: 2,
              py: 1.5,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center" }}>
              {dependency.ssvcPriority && (
                <SSVCPriorityStatusChip displaySSVCPriority={dependency.ssvcPriority} />
              )}
            </Box>
            <Typography
              noWrap
              sx={{ color: slate[800], fontSize: 14, fontWeight: 700, minWidth: 0 }}
            >
              {dependency.name}
            </Typography>
            <Typography noWrap sx={{ color: slate[600], fontSize: 14 }}>
              {dependency.version || "-"}
            </Typography>
            <Box>
              <Chip
                label={dependency.type}
                size="small"
                sx={{ bgcolor: slate[100], color: slate[600], fontSize: 12, fontWeight: 600 }}
              />
            </Box>
            <Typography noWrap sx={{ color: slate[600], fontSize: 14 }}>
              {dependency.license || "-"}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}

export function DependenciesCard({
  filteredDependencies,
  onUpdateClick,
  onPackageClick,
  pageEndIndex,
  pageSize,
  pageStartIndex,
  paginatedDependencies,
  query,
  safeCurrentPage,
  setCurrentPage,
  setPageSize,
  setQuery,
  totalPages,
}) {
  const { t } = useTranslation("status", { keyPrefix: "DependenciesCard" });

  return (
    <Card
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 6,
        boxShadow: "none",
        minWidth: 0,
      }}
    >
      <CardContent sx={{ minWidth: 0, p: 3 }}>
        <Box
          sx={{
            border: `1px solid ${slate[200]}`,
            borderRadius: 4,
            minWidth: 0,
            overflow: "hidden",
            width: "100%",
          }}
        >
          <Box
            sx={{
              bgcolor: "rgba(248, 250, 252, 0.7)",
              borderBottom: `1px solid ${slate[200]}`,
              display: "flex",
              flexDirection: "column",
              gap: 0.5,
              px: 1.5,
              py: 1.25,
            }}
          >
            <Box
              sx={{
                bgcolor: "white",
                border: `1px solid ${slate[200]}`,
                borderRadius: 3,
                boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
                height: 36,
                maxWidth: 520,
                position: "relative",
                width: "100%",
              }}
            >
              <SearchIcon
                sx={{
                  color: slate[400],
                  fontSize: 17,
                  left: 12,
                  pointerEvents: "none",
                  position: "absolute",
                  top: "50%",
                  transform: "translateY(-50%)",
                }}
              />
              <Box
                component="input"
                onChange={(event) => {
                  setCurrentPage(1);
                  setQuery(event.target.value);
                }}
                placeholder={t("searchPlaceholder")}
                sx={{
                  "&::placeholder": { color: slate[400], opacity: 1 },
                  bgcolor: "transparent",
                  border: 0,
                  boxSizing: "border-box",
                  color: slate[700],
                  display: "block",
                  font: "inherit",
                  fontSize: 13,
                  height: "100%",
                  lineHeight: "18px",
                  outline: "none",
                  pl: "34px",
                  pr: 1.25,
                  py: 0,
                  width: "100%",
                }}
                value={query}
              />
            </Box>
            <Box sx={{ alignItems: "center", display: "flex" }}>
              <Typography
                sx={{
                  color: slate[500],
                  fontSize: 13,
                  lineHeight: "18px",
                  whiteSpace: "nowrap",
                }}
              >
                {filteredDependencies.length === 0
                  ? t("noDependencies")
                  : t("pagingRange", {
                      total: filteredDependencies.length,
                      start: pageStartIndex + 1,
                      end: pageEndIndex,
                    })}
              </Typography>
              <AppButton
                onClick={onUpdateClick}
                size="small"
                startIcon={<UploadFileIcon />}
                sx={{
                  bgcolor: "white",
                  ml: "auto",
                }}
                variant="outlined"
              >
                {t("updateSbom")}
              </AppButton>
            </Box>
          </Box>

          <Box sx={{ minWidth: 0, overflowX: "auto", width: "100%" }}>
            <Box sx={{ minWidth: { lg: 0, xs: 640 }, width: "100%" }}>
              <Box
                sx={{
                  bgcolor: slate[50],
                  color: slate[500],
                  display: "grid",
                  fontSize: 12,
                  fontWeight: 700,
                  gridTemplateColumns: "48px 1.4fr 0.7fr 0.65fr 0.8fr",
                  letterSpacing: 0,
                  px: 2,
                  py: 1.5,
                }}
              >
                <Box>SSVC</Box>
                <Box>{t("package")}</Box>
                <Box>{t("version")}</Box>
                <Box>{t("type")}</Box>
                <Box>{t("license")}</Box>
              </Box>
              <DependencyTable
                dependencies={paginatedDependencies}
                onPackageClick={onPackageClick}
                pageStartIndex={pageStartIndex}
              />
            </Box>
          </Box>

          {filteredDependencies.length > 0 && (
            <Box
              sx={{
                alignItems: { md: "center" },
                bgcolor: "white",
                borderTop: `1px solid ${slate[200]}`,
                display: "flex",
                flexDirection: { md: "row", xs: "column" },
                gap: 1.5,
                justifyContent: "space-between",
                px: 2,
                py: 1.25,
              }}
            >
              <Box
                sx={{
                  alignItems: "center",
                  color: slate[500],
                  display: "flex",
                  flexShrink: 0,
                  gap: 1.25,
                  minHeight: 34,
                }}
              >
                <Typography
                  sx={{
                    color: slate[500],
                    fontSize: 13,
                    lineHeight: "18px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {t("rowsPerPage")}
                </Typography>
                <Select
                  onChange={(event) => {
                    setCurrentPage(1);
                    setPageSize(Number(event.target.value));
                  }}
                  size="small"
                  sx={compactSelectSx}
                  value={pageSize}
                >
                  <MenuItem value={10}>10</MenuItem>
                  <MenuItem value={20}>20</MenuItem>
                  <MenuItem value={50}>50</MenuItem>
                </Select>
              </Box>
              <Box
                sx={{
                  alignItems: "center",
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 1.25,
                  justifyContent: { md: "flex-end", xs: "space-between" },
                  minWidth: 0,
                }}
              >
                <Typography
                  sx={{
                    color: slate[600],
                    flexShrink: 0,
                    fontSize: 13,
                    fontWeight: 600,
                    lineHeight: "18px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {t("pagingPosition", { current: safeCurrentPage, total: totalPages })}
                </Typography>
                <Stack direction="row" alignItems="center" sx={{ gap: 0.75 }}>
                  <AppButton
                    disabled={safeCurrentPage <= 1}
                    onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                    size="small"
                    startIcon={<ChevronLeftIcon />}
                    variant="outlined"
                  >
                    {t("prev")}
                  </AppButton>
                  <AppButton
                    disabled={safeCurrentPage >= totalPages}
                    onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                    size="small"
                    endIcon={<ChevronRightIcon />}
                    variant="outlined"
                  >
                    {t("next")}
                  </AppButton>
                </Stack>
              </Box>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
