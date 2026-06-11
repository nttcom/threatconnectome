import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Stack, Typography, useMediaQuery, useTheme } from "@mui/material";

import { IconBadge } from "./IconBadge";
import { IconRenderer } from "./IconRenderer";
import { MenuTriggerButton } from "./MenuTriggerButton";
import {
  colors,
  compactTopbarButtonSx,
  ellipsisTextSx,
  responsiveTopbarButtonSx,
  topbarButtonContentSx,
} from "./topbarStyles";

export function PageMenuButton({ active, currentPage, labels, onClick }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const compactLabel = currentPage.shortLabel ?? currentPage.label;

  if (isMobile) {
    return (
      <MenuTriggerButton
        active={active}
        ariaLabel={labels.pageMenu}
        onClick={onClick}
        sx={compactTopbarButtonSx}
      >
        <IconBadge
          icon={currentPage.icon}
          size={28}
          iconSize={18}
          radius={8}
          tone={currentPage.tone}
        />
      </MenuTriggerButton>
    );
  }

  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.pageMenu}
      onClick={onClick}
      sx={{
        ...responsiveTopbarButtonSx,
        maxWidth: { sm: 168, md: 220 },
        minWidth: 0,
        gap: 0.5,
      }}
    >
      <Stack direction="row" sx={topbarButtonContentSx}>
        <IconBadge
          icon={currentPage.icon}
          size={24}
          iconSize={15}
          radius={6}
          tone={currentPage.tone}
        />
        <Typography
          noWrap
          sx={{
            display: { xs: "none", sm: "block", md: "none" },
            minWidth: 0,
            fontSize: 14,
            fontWeight: 600,
            ...ellipsisTextSx,
          }}
        >
          {compactLabel}
        </Typography>
        <Typography
          noWrap
          sx={{
            display: { xs: "none", md: "block" },
            minWidth: 0,
            fontSize: 14,
            fontWeight: 600,
            ...ellipsisTextSx,
          }}
        >
          {currentPage.label}
        </Typography>
        <Box sx={{ color: colors.ink400, flexShrink: 0 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}
