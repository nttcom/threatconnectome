import type { Location, NavigateFunction } from "react-router-dom";

import type { UserResponse } from "../../types/types.gen";

import { LocationReader } from "./LocationReader";

type UserMe = Pick<UserResponse, "pteam_roles"> & {
  default_pteam_id?: UserResponse["default_pteam_id"];
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
