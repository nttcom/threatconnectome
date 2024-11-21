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

  isTopicsPage() {
    return this.location.pathname.includes("/topics");
  }

  isAccountPage() {
    return this.location.pathname === "/account";
  }

  getTeamMode() {
    if (this.isStatusPage() || this.isTagPage() || this.isPTeamPage()) {
      return "pteam";
    } else if (this.isTopicsPage() || this.isAccountPage()) {
      const params = new URLSearchParams(this.location.search);
      if (params.get("pteamId")) {
        return "pteam";
      }
    }
    return "pteam";
  }

  isPTeamMode() {
    return this.getTeamMode() === "pteam";
  }

  getPTeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
