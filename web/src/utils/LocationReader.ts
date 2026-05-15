type LocationLike = {
  pathname: string;
  search: string;
};

export class LocationReader {
  private location: LocationLike;

  constructor(location: LocationLike) {
    this.location = location;
  }

  isStatusPage(): boolean {
    return this.location.pathname === "/";
  }

  isPackagePage(): boolean {
    return /\/packages\//.test(this.location.pathname);
  }

  isPTeamPage(): boolean {
    return this.location.pathname === "/pteam";
  }

  isVulnsPage(): boolean {
    return this.location.pathname.includes("/vulns");
  }

  isEoLPage(): boolean {
    return this.location.pathname.includes("/eol");
  }

  isToDoPage(): boolean {
    return this.location.pathname === "/todo";
  }

  getPTeamId(): string | null {
    const params = new URLSearchParams(this.location.search);
    return params.get("pteamId");
  }
}
