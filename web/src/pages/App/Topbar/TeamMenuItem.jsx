import CheckIcon from "@mui/icons-material/Check";
import { Box, MenuItem, Typography } from "@mui/material";

import { IconRenderer } from "./IconRenderer";
import { colors, compactMenuItemSx } from "./topbarStyles";

export function TeamMenuItem({ item, onSelectTeam }) {
  return (
    <MenuItem
      onClick={() => onSelectTeam(item.id)}
      sx={{
        ...compactMenuItemSx,
        justifyContent: "space-between",
        gap: 2,
        bgcolor: item.current ? colors.slate50 : "transparent",
        "&:hover": { bgcolor: colors.slate50 },
      }}
    >
      <Box sx={{ minWidth: 0 }}>
        <Typography sx={{ color: colors.ink900, fontSize: 14, fontWeight: 600 }}>
          {item.name}
        </Typography>
        {item.detail ? (
          <Typography sx={{ color: colors.ink500, fontSize: 12, lineHeight: 1.7 }}>
            {item.detail}
          </Typography>
        ) : null}
      </Box>
      {item.current ? <IconRenderer icon={CheckIcon} size={18} /> : null}
    </MenuItem>
  );
}
