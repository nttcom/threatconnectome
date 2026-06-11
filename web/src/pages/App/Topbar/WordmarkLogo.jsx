import { Stack, Typography } from "@mui/material";

import { MarkLogo } from "./MarkLogo";
import { colors } from "./topbarStyles";

export function WordmarkLogo() {
  return (
    <Stack direction="row" sx={{ alignItems: "center", gap: 1 }}>
      <MarkLogo />
      <Typography
        sx={{
          fontFamily: '"Inter", sans-serif',
          fontSize: 16,
          fontWeight: 700,
          color: colors.ink900,
          letterSpacing: 0,
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        Threatconnectome
      </Typography>
    </Stack>
  );
}
