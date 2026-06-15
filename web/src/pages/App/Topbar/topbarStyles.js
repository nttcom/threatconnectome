import { uiPalette, uiRadii, uiShadows } from "../../../styles/designTokens";

export const colors = {
  ink900: uiPalette.gray[900],
  ink700: uiPalette.gray[700],
  ink500: uiPalette.gray[500],
  ink400: uiPalette.gray[400],
  slate50: uiPalette.slate[50],
  slate100: uiPalette.slate[100],
  slate200: uiPalette.slate[200],
  slate300: uiPalette.slate[300],
  brand50: uiPalette.brand[50],
  brand100: uiPalette.brand[100],
  brand700: uiPalette.brand[700],
  red50: uiPalette.red[50],
  red100: uiPalette.red[100],
  red600: uiPalette.red[600],
  amber50: uiPalette.amber[50],
  amber100: uiPalette.amber[100],
  amber700: uiPalette.amber[700],
  sky50: uiPalette.sky[50],
  sky100: uiPalette.sky[100],
  sky700: uiPalette.sky[700],
  violet50: uiPalette.violet[50],
  violet100: uiPalette.violet[100],
  violet700: uiPalette.violet[700],
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
  borderRadius: uiRadii.popover,
  boxShadow: uiShadows.topbarMenu,
  overflow: "hidden",
};

export const controlButtonSx = {
  height: 40,
  minHeight: 40,
  borderColor: `${colors.slate300} !important`,
  color: colors.ink700,
  bgcolor: "#fff",
  borderRadius: uiRadii.topbarControl,
  boxShadow: uiShadows.xs,
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
  borderRadius: uiRadii.menuItem,
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
    borderRadius: uiRadii.pill,
    bgcolor: colors.ink400,
    border: "2px solid transparent",
    backgroundClip: "content-box",
  },
  "&::-webkit-scrollbar-track": {
    bgcolor: "transparent",
  },
};
