export class LocationReader {
  constructor(location) {
    this.location = location;
  }

  isStatusPage() {
    return this.location.pathname === "/";
  }

  isPackagePage() {
    return /\/packages\//.test(this.location.pathname);
  }

  isPTeamPage() {
    return this.location.pathname === "/pteam";
  }

  isPTeamInvitationPage() {
    return this.location.pathname === "/pteam/join";
  }

  isTopicsPage() {
    return this.location.pathname.includes("/topics");
  }

  isVulnerabilitiesPage() {
    return this.location.pathname.includes("/vulnerabilities");
  }

  getPTeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
