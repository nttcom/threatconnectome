import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import GroupIcon from "@mui/icons-material/Group";
import { Box, Stack, Typography } from "@mui/material";

import { IconBadge } from "./IconBadge";
import { IconRenderer } from "./IconRenderer";
import { MenuTriggerButton } from "./MenuTriggerButton";
import { colors, responsiveTopbarButtonSx, topbarButtonContentSx } from "./topbarStyles";

export function TeamMenuButton({ active, currentTeam, labels, onClick }) {
  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.teamMenu}
      onClick={onClick}
      sx={responsiveTopbarButtonSx}
    >
      <Stack direction="row" sx={topbarButtonContentSx}>
        <IconBadge icon={GroupIcon} size={24} iconSize={15} radius={6} />
        <Typography
          noWrap
          sx={{
            display: { xs: "none", sm: "block" },
            maxWidth: 144,
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          {currentTeam?.name ?? labels.noTeam}
        </Typography>
        <Box sx={{ display: { xs: "none", sm: "flex" }, color: colors.ink400 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}
