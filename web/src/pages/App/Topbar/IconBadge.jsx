import { Box } from "@mui/material";

import { IconRenderer } from "./IconRenderer";
import { tonePalette } from "./topbarStyles";

export function IconBadge({ icon, size = 32, iconSize = 18, radius = 8, tone = "slate" }) {
  const palette = tonePalette[tone];

  return (
    <Box
      sx={{
        display: "grid",
        placeItems: "center",
        width: size,
        height: size,
        flexShrink: 0,
        borderRadius: `${radius}px`,
        bgcolor: palette.bg,
        color: palette.color,
        border: `1px solid ${palette.ring}`,
      }}
    >
      <IconRenderer icon={icon} size={iconSize} />
    </Box>
  );
}
