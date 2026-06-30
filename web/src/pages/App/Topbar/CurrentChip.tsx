import { Chip } from "@mui/material";

import { colors, currentChipSx } from "./topbarStyles";
import type { Sx } from "./topbarTypes";

type CurrentChipProps = {
  label: string;
  sx?: Sx;
};

export function CurrentChip({ label, sx }: CurrentChipProps) {
  return (
    <Chip
      label={label}
      size="small"
      sx={{
        ...currentChipSx,
        bgcolor: colors.brand50,
        color: colors.brand700,
        border: `1px solid ${colors.brand100}`,
        ...sx,
      }}
    />
  );
}
