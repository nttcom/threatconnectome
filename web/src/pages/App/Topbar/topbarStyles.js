export const colors = {
  ink900: "#111827",
  ink700: "#374151",
  ink500: "#6B7280",
  ink400: "#9CA3AF",
  slate50: "#F8FAFC",
  slate100: "#F1F5F9",
  slate200: "#E2E8F0",
  slate300: "#CBD5E1",
  brand50: "#ECFDF5",
  brand100: "#D1FAE5",
  brand700: "#047857",
  red50: "#FEF2F2",
  red100: "#FEE2E2",
  red600: "#DC2626",
  amber50: "#FFFBEB",
  amber100: "#FEF3C7",
  amber700: "#B45309",
  sky50: "#F0F9FF",
  sky100: "#E0F2FE",
  sky700: "#0369A1",
  violet50: "#F5F3FF",
  violet100: "#EDE9FE",
  violet700: "#6D28D9",
};

export const tonePalette = {
  brand: { bg: colors.brand50, color: colors.brand700, ring: colors.brand100 },
  sky: { bg: colors.sky50, color: colors.sky700, ring: colors.sky100 },
  red: { bg: colors.red50, color: colors.red600, ring: colors.red100 },
  amber: { bg: colors.amber50, color: colors.amber700, ring: colors.amber100 },
  violet: { bg: colors.violet50, color: colors.violet700, ring: colors.violet100 },
  slate: { bg: "#fff", color: colors.ink500, ring: colors.slate200 },
};

export const menuWidths = {
  page: { xs: "calc(100vw - 16px)", sm: 336 },
  default: { xs: "calc(100vw - 16px)", sm: 288 },
};

export const menuPaperSx = {
  mt: 1,
  border: `1px solid ${colors.slate200}`,
  borderRadius: 3,
  boxShadow: "0 18px 44px rgba(17, 24, 39, 0.14), 0 2px 8px rgba(17, 24, 39, 0.08)",
  overflow: "hidden",
};

export const controlButtonSx = {
  height: 40,
  minHeight: 40,
  borderColor: `${colors.slate300} !important`,
  color: colors.ink700,
  bgcolor: "#fff",
  borderRadius: "8px",
  boxShadow: "0 1px 2px rgba(17, 24, 39, 0.05)",
  textTransform: "none",
  fontWeight: 600,
  lineHeight: 1,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  "& .MuiButton-endIcon": {
    ml: 0.75,
    mr: 0,
    color: colors.ink400,
  },
  "&:hover": {
    borderColor: `${colors.slate300} !important`,
    bgcolor: colors.slate50,
  },
  "&:focus-visible": {
    outline: `2px solid ${colors.brand100}`,
    outlineOffset: 2,
  },
};

export const compactTopbarButtonSx = {
  ...controlButtonSx,
  width: 40,
  height: 40,
  minWidth: 40,
  px: 0,
};

export const responsiveTopbarButtonSx = {
  ...controlButtonSx,
  minWidth: { xs: 40, sm: 0 },
  width: { xs: 40, sm: "auto" },
  px: { xs: 0, sm: 1.5 },
};

export const topbarButtonContentSx = {
  alignItems: "center",
  gap: 1,
  minWidth: 0,
  maxWidth: "100%",
  overflow: "hidden",
};

export const ellipsisTextSx = {
  textOverflow: "ellipsis",
  overflow: "hidden",
  whiteSpace: "nowrap",
};

export const compactMenuItemSx = {
  mx: 0.75,
  my: 0.25,
  px: 1.5,
  py: 1.25,
  borderRadius: 2,
};

export const currentChipSx = {
  height: 20,
  fontSize: 11,
  fontWeight: 600,
};

export const teamMenuListSx = {
  maxHeight: 252,
  overflowY: "auto",
  overscrollBehavior: "contain",
  py: 0.25,
  scrollbarWidth: "thin",
  scrollbarColor: `${colors.ink400} transparent`,
  "&::-webkit-scrollbar": {
    width: 8,
  },
  "&::-webkit-scrollbar-thumb": {
    borderRadius: 999,
    bgcolor: colors.ink400,
    border: "2px solid transparent",
    backgroundClip: "content-box",
  },
  "&::-webkit-scrollbar-track": {
    bgcolor: "transparent",
  },
};
