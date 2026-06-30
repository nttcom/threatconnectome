import { Box } from "@mui/material";
import type { MouseEvent } from "react";

import { MarkLogo } from "./MarkLogo";
import { WordmarkLogo } from "./WordmarkLogo";

type TopbarLogoLinkProps = {
  ariaLabel: string;
  onClick: (event: MouseEvent<HTMLAnchorElement>) => void;
};

export function TopbarLogoLink({ ariaLabel, onClick }: TopbarLogoLinkProps) {
  return (
    <Box
      component="a"
      href="/"
      aria-label={ariaLabel}
      onClick={onClick}
      sx={{
        display: "flex",
        alignItems: "center",
        height: 40,
        flexShrink: 0,
        textDecoration: "none",
      }}
    >
      <Box sx={{ display: { xs: "block", sm: "none" }, lineHeight: 0 }}>
        <MarkLogo size={38} framed={false} />
      </Box>
      <Box sx={{ display: { xs: "none", sm: "block" } }}>
        <WordmarkLogo />
      </Box>
    </Box>
  );
}
