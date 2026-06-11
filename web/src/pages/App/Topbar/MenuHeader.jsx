import { Box, Typography } from "@mui/material";

import { colors } from "./topbarStyles";

export function MenuHeader({ title, detail }) {
  return (
    <Box sx={{ px: 2, py: 1.5, borderBottom: `1px solid ${colors.slate100}` }}>
      <Typography
        sx={{
          color: colors.ink500,
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: 0.7,
          textTransform: "uppercase",
        }}
      >
        {title}
      </Typography>
      {detail ? (
        <Typography sx={{ mt: 0.25, color: colors.ink400, fontSize: 12 }}>{detail}</Typography>
      ) : null}
    </Box>
  );
}
