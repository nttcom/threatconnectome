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

  isAnalysisPage() {
    return this.location.pathname === "/analysis";
  }

  isATeamPage() {
    return this.location.pathname === "/ateam";
  }

  isPTeamInvitationPage() {
    return this.location.pathname === "/ateam/join";
  }

  isWatchingRequestPage() {
    return this.location.pathname === "/pteam/watching_request";
  }

  isTopicsPage() {
    return this.location.pathname.includes("/topics");
  }

  isAccountPage() {
    return this.location.pathname === "/account";
  }

  getTeamMode() {
    if (this.isAnalysisPage() || this.isATeamPage()) {
      return "ateam";
    } else if (this.isStatusPage() || this.isTagPage() || this.isPTeamPage()) {
      return "pteam";
    } else if (this.isTopicsPage() || this.isAccountPage()) {
      const params = new URLSearchParams(this.location.search);
      if (params.get("ateamId")) {
        return "ateam";
      } else if (params.get("pteamId")) {
        return "pteam";
      }
    }
    return "pteam";
  }

  isATeamMode() {
    return this.getTeamMode() === "ateam";
  }

  isPTeamMode() {
    return this.getTeamMode() === "pteam";
  }

  getATeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("ateamId");
  }

  getPTeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
