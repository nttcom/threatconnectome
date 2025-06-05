import { LocationReader } from "./LocationReader";

export const navigateSpecifiedPteam = (location, pteam_roles, navigate) => {
  const params = new URLSearchParams(location.search);
  const locationReader = new LocationReader(location);

  if (
    locationReader.isStatusPage() ||
    locationReader.isPackagePage() ||
    locationReader.isPTeamPage()
  ) {
    if (!pteam_roles.length > 0) {
      if (params.get("pteamId")) {
        navigate(location.pathname);
      }
      return;
    }
    const pteamIdx = params.get("pteamId") || pteam_roles[0].pteam.pteam_id;
    if (params.get("pteamId") !== pteamIdx) {
      params.set("pteamId", pteamIdx);
      navigate(location.pathname + "?" + params.toString());
    }
  }
};
