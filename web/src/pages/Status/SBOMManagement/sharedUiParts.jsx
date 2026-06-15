/* eslint-disable react/prop-types */
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Button, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { collapseSpaces } from "../../../utils/displayText";

import {
  sectionIconBoxSx,
  sectionTitleTextSx,
  slate,
  tabButtonSx,
  textButtonSx,
  uiRadii,
  uiTransitions,
} from "./styleTokens";

export function CountBadge({ children }) {
  return (
    <Box
      component="span"
      sx={{
        alignItems: "center",
        bgcolor: slate[100],
        borderRadius: uiRadii.pill,
        color: slate[600],
        display: "inline-flex",
        flexShrink: 0,
        fontSize: 12,
        fontWeight: 700,
        height: 32,
        justifyContent: "center",
        lineHeight: 1,
        px: 1.25,
      }}
    >
      {children}
    </Box>
  );
}

export function HeaderActionButton({ active = false, children, icon: Icon, sx, ...props }) {
  return (
    <Box
      component="button"
      type="button"
      sx={{
        "&:disabled": {
          cursor: "default",
          opacity: 0.5,
        },
        alignItems: "center",
        bgcolor: active ? slate[950] : "white",
        border: `1px solid ${active ? slate[950] : slate[300]}`,
        borderRadius: uiRadii.pill,
        color: active ? "white" : slate[900],
        cursor: "pointer",
        display: "inline-flex",
        flexShrink: 0,
        font: "inherit",
        fontSize: 13,
        fontWeight: 700,
        gap: 0.75,
        height: 32,
        justifyContent: "center",
        lineHeight: 1,
        minWidth: 0,
        px: 1.5,
        whiteSpace: "nowrap",
        ...sx,
      }}
      {...props}
    >
      {Icon && <Icon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />}
      <Box component="span" sx={{ display: "block", lineHeight: 1 }}>
        {children}
      </Box>
    </Box>
  );
}

export function AppButton({ size = "medium", sx, variant = "contained", ...props }) {
  const muiSize = size === "xs" || size === "sm" ? "small" : size;

  return (
    <Button
      size={muiSize}
      sx={{
        ...textButtonSx,
        height: size === "xs" ? 32 : muiSize === "small" ? 34 : 40,
        minHeight: size === "xs" ? 32 : muiSize === "small" ? 34 : 40,
        px: size === "xs" ? 1.25 : muiSize === "small" ? 1.5 : 2,
        ...sx,
      }}
      variant={variant}
      {...props}
    />
  );
}

export function TabButton({ active, onClick, sbom }) {
  const { t } = useTranslation("status", { keyPrefix: "sharedUiParts" });
  return (
    <Box
      component="button"
      onClick={onClick}
      sx={{
        "&:hover": {
          backgroundColor: active ? "white" : slate[200],
          color: active ? slate[950] : slate[800],
        },
        backgroundColor: active ? "white" : slate[100],
        border: "1px solid",
        borderColor: active ? slate[200] : "transparent",
        color: active ? slate[950] : slate[500],
        cursor: "pointer",
        font: "inherit",
        fontSize: 14,
        fontWeight: 600,
        px: 2.5,
        py: 1.5,
        ...tabButtonSx,
        boxShadow: active ? tabButtonSx.boxShadow : "none",
      }}
      type="button"
    >
      {collapseSpaces(sbom.title) || t("untitledSbom")}
    </Box>
  );
}

export function AccordionHeader({ action, icon: Icon, onToggle, open, title }) {
  return (
    <Box sx={{ alignItems: "center", display: "flex", gap: 1.5, height: 44, px: 2 }}>
      <Box
        component="button"
        onClick={onToggle}
        sx={{
          alignItems: "center",
          background: "transparent",
          border: 0,
          color: "inherit",
          cursor: "pointer",
          display: "flex",
          flex: "1 1 auto",
          font: "inherit",
          gap: 1,
          height: 32,
          minWidth: 0,
          p: 0,
          pointerEvents: { md: "none" },
          textAlign: "left",
        }}
        type="button"
      >
        <Stack direction="row" alignItems="center" sx={{ gap: 1, height: 32, minWidth: 0 }}>
          <Box sx={{ ...sectionIconBoxSx, height: 32 }}>
            <Icon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />
          </Box>
          <Typography
            noWrap
            sx={{
              ...sectionTitleTextSx,
              alignItems: "center",
              display: "inline-flex",
              height: 32,
              lineHeight: 1,
            }}
          >
            {title}
          </Typography>
        </Stack>
        <ExpandMoreIcon
          sx={{
            color: slate[400],
            display: { md: "none", xs: "block" },
            flexShrink: 0,
            fontSize: 22,
            height: 22,
            ml: "auto",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: uiTransitions.transform,
            width: 22,
          }}
        />
      </Box>
      <Box
        sx={{
          alignItems: "center",
          display: "flex",
          flexShrink: 0,
          height: 32,
          justifyContent: "flex-end",
          minWidth: 0,
        }}
      >
        {action}
      </Box>
    </Box>
  );
}
