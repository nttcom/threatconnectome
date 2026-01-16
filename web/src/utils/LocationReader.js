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

  isVulnsPage() {
    return this.location.pathname.includes("/vulns");
  }

  isEoLPage() {
    return this.location.pathname.includes("/eol");
  }

  isToDoPage() {
    return this.location.pathname === "/todo";
  }

  getPTeamId() {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
