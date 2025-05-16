export class LocationReader {
  constructor(location) {
    this.location = location;
  }

  isStatusPage() {
    return this.location.pathname === "/";
  }

  isTagPage() {
    return /\/tags\//.test(this.location.pathname);
  }

  isPTeamPage() {
    return this.location.pathname === "/pteam";
  }

  isPTeamInvitationPage() {
    return this.location.pathname === "/pteam/join";
  }

  isVulnsPage() {
    return this.location.pathname.includes("/vulns");
  }

  isVulnerabilitiesPage() {
    return this.location.pathname.includes("/vulnerabilities");
  }

  getPTeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
