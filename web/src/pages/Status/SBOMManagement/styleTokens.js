export const slate = {
  50: "#f8fafc",
  100: "#f1f5f9",
  200: "#e2e8f0",
  300: "#cbd5e1",
  400: "#94a3b8",
  500: "#64748b",
  600: "#475569",
  700: "#334155",
  800: "#1e293b",
  900: "#0f172a",
  950: "#020617",
};

export const fieldSx = {
  "& .MuiOutlinedInput-root": {
    backgroundColor: "white",
    borderRadius: 4,
    boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
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
  borderRadius: 3,
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
  borderRadius: 3,
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
