import { Box, MenuItem, Stack, Typography } from "@mui/material";

import { CurrentChip } from "./CurrentChip";
import { IconBadge } from "./IconBadge";
import { colors, compactMenuItemSx } from "./topbarStyles";
import type { TopbarLabels, TopbarPageItem } from "./topbarTypes";

type PageMenuItemProps = {
  current: boolean;
  item: TopbarPageItem;
  labels: TopbarLabels;
  onSelect: (item: TopbarPageItem) => void;
};

export function PageMenuItem({ current, item, labels, onSelect }: PageMenuItemProps) {
  return (
    <MenuItem
      selected={current}
      onClick={() => onSelect(item)}
      sx={{
        ...compactMenuItemSx,
        alignItems: "center",
        gap: 1.5,
        whiteSpace: "normal",
        bgcolor: current ? colors.brand50 : "transparent",
        outline: current ? `1px solid ${colors.brand100}` : "none",
        "&.Mui-selected": {
          bgcolor: colors.brand50,
        },
        "&.Mui-selected:hover": {
          bgcolor: colors.brand50,
        },
        "&:hover": { bgcolor: current ? colors.brand50 : colors.slate50 },
      }}
    >
      <IconBadge icon={item.icon} tone={item.tone} />
      <Box sx={{ minWidth: 0 }}>
        <Stack direction="row" sx={{ alignItems: "center", gap: 1, flexWrap: "wrap" }}>
          <Typography sx={{ color: colors.ink900, fontSize: 14, fontWeight: 600 }}>
            {item.label}
          </Typography>
          {current ? <CurrentChip label={labels.current} sx={{ bgcolor: "#fff" }} /> : null}
        </Stack>
      </Box>
    </MenuItem>
  );
}
