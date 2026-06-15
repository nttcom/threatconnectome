import { uiPalette, uiRadii, uiShadows, uiTransitions } from "../../../styles/designTokens";

export const slate = uiPalette.slate;

export const fieldSx = {
  "& .MuiOutlinedInput-root": {
    backgroundColor: "white",
    borderRadius: uiRadii.field,
    boxShadow: uiShadows.xs,
    fontSize: 14,
  },
};

export const labelSx = {
  color: slate[500],
  fontSize: 12,
  fontWeight: 700,
  letterSpacing: 0,
  textTransform: "uppercase",
};

export const textButtonSx = {
  "& .MuiButton-endIcon": { ml: 0.75 },
  "& .MuiButton-startIcon": { mr: 0.75 },
  borderRadius: uiRadii.statusButton,
  fontWeight: 600,
  lineHeight: 1,
  textTransform: "none",
  whiteSpace: "nowrap",
};

export const compactSelectSx = {
  "& .MuiSelect-select": {
    alignItems: "center",
    display: "flex",
    minHeight: 0,
    py: 0,
  },
  borderRadius: uiRadii.statusButton,
  color: slate[700],
  fontSize: 13,
  height: 32,
  minWidth: 72,
};

export const sectionIconBoxSx = {
  alignItems: "center",
  color: slate[700],
  display: "flex",
  flexShrink: 0,
  height: 20,
  justifyContent: "center",
  lineHeight: 0,
  width: 20,
};

export const sectionTitleTextSx = {
  color: slate[700],
  display: "block",
  fontSize: 16,
  fontWeight: 700,
  letterSpacing: 0,
  lineHeight: "20px",
};

export const statusCardSx = {
  border: `1px solid ${slate[200]}`,
  borderRadius: uiRadii.statusCard,
  boxShadow: "none",
  minWidth: 0,
};

export const tabButtonSx = {
  borderTopLeftRadius: 16,
  borderTopRightRadius: 16,
  boxShadow: uiShadows.xs,
  transition: uiTransitions.colorAndBorder,
  whiteSpace: "nowrap",
};

export const tabPanelSx = {
  bgcolor: "white",
  borderBottomLeftRadius: 24,
  borderBottomRightRadius: 24,
  borderTopRightRadius: 24,
  boxShadow: uiShadows.xs,
  minWidth: 0,
  width: "100%",
};

export const surfaceShadowSx = {
  boxShadow: uiShadows.xs,
};

export const floatingSurfaceSx = {
  boxShadow: uiShadows.floating,
};

export { uiRadii, uiShadows, uiTransitions };
