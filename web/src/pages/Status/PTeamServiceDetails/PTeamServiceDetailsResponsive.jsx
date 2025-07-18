import { useTheme, useMediaQuery } from "@mui/material";

import { PTeamServiceDetails } from "./PTeamServiceDetailsDesktop";
import { PTeamServiceDetailsMobile } from "./PTeamServiceDetailsMobile";

export function PTeamServiceDetailsResponsive(props) {
  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  return isMdDown ? <PTeamServiceDetailsMobile {...props} /> : <PTeamServiceDetails {...props} />;
}
