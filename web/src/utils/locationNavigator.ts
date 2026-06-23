import type { Location } from "react-router-dom";

import { LocationReader } from "./LocationReader";

type UserMe = {
  pteam_roles: Array<{ pteam: { pteam_id: string } }>;
  default_pteam_id?: string | null;
};

export const getSpecifiedPteamNavigationTarget = (
  location: Pick<Location, "pathname" | "search">,
  userMe: UserMe,
): string | null => {
  const params = new URLSearchParams(location.search);
  const locationReader = new LocationReader(location);

  const needsPteam =
    locationReader.isStatusPage() || locationReader.isPackagePage() || locationReader.isPTeamPage();

  if (!needsPteam) return null;

  const currentPteamId = params.get("pteamId");
  const pteamIds = userMe.pteam_roles.map((pteamRole) => pteamRole.pteam.pteam_id);

  if (pteamIds.length === 0) {
    return currentPteamId ? location.pathname : null;
  }

  const defaultPteamId = userMe.default_pteam_id;
  const pteamId =
    currentPteamId && pteamIds.includes(currentPteamId)
      ? currentPteamId
      : defaultPteamId && pteamIds.includes(defaultPteamId)
        ? defaultPteamId
        : pteamIds[0];

  if (currentPteamId === pteamId) return null;

  params.set("pteamId", pteamId);
  return location.pathname + "?" + params.toString();
};
