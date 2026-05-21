import type { Location, NavigateFunction } from "react-router-dom";

import { LocationReader } from "./LocationReader";

type UserMe = {
  pteam_roles: Array<{ pteam: { pteam_id: string } }>;
  default_pteam_id?: string | null;
};

export const navigateSpecifiedPteam = (
  location: Pick<Location, "pathname" | "search">,
  userMe: UserMe,
  navigate: NavigateFunction,
): void => {
  const params = new URLSearchParams(location.search);
  const locationReader = new LocationReader(location);

  if (
    locationReader.isStatusPage() ||
    locationReader.isPackagePage() ||
    locationReader.isPTeamPage()
  ) {
    if (userMe.pteam_roles.length === 0) {
      if (params.get("pteamId")) {
        navigate(location.pathname);
      }
      return;
    }
    const pteamIdx =
      params.get("pteamId") || userMe.default_pteam_id || userMe.pteam_roles[0].pteam.pteam_id;
    if (params.get("pteamId") !== pteamIdx) {
      params.set("pteamId", pteamIdx);
      navigate(location.pathname + "?" + params.toString());
    }
  }
};
