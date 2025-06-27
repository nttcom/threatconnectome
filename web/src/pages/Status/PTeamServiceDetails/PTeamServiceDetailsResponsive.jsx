import { useTheme, useMediaQuery } from "@mui/material";

import { PTeamServiceDetails } from "./PTeamServiceDetailsDesktop";
import { PTeamServiceDetailsMobile } from "./PTeamServiceDetailsMobile";

export function PTeamServiceDetailsResponsive(props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return isMobile ? <PTeamServiceDetailsMobile {...props} /> : <PTeamServiceDetails {...props} />;
}
