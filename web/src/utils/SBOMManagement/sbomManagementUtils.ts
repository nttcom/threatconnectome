import type { PTeamPackageVersionSummary, PTeamServiceResponse } from "../../../types/types.gen";
import type {
  SbomDependency,
  SbomService,
  SbomServiceTab,
} from "../../pages/Status/SBOMManagement/SBOMManagementTypes";

export const NEW_SBOM_ID = "__new_sbom__";

export function createId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

export function normalizeCommaSeparatedValues(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function getNextActiveIdAfterRemoval(items: SbomServiceTab[], removedId: string) {
  const removedIndex = items.findIndex((item) => item.id === removedId);
  const remaining = items.filter((item) => item.id !== removedId);

  if (remaining.length === 0) {
    return "";
  }

  if (removedIndex < 0) {
    return remaining[0].id;
  }

  return remaining[Math.min(removedIndex, remaining.length - 1)].id;
}

export function isDeleteConfirmationValid(input: string, title: string) {
  return input.trim() === title;
}

export function buildServiceTabsFromPTeam(services: PTeamServiceResponse[]): SbomServiceTab[] {
  if (!Array.isArray(services)) return [];

  return services.map((service) => ({
    id: service.service_id,
    title: service.service_name,
  }));
}

export function buildCurrentServiceFromPTeam(
  services: PTeamServiceResponse[],
  currentServiceId: string | null,
  imageUrl = "",
): SbomService | null {
  if (!Array.isArray(services) || !currentServiceId) return null;

  const service = services.find((item) => item.service_id === currentServiceId);
  if (!service) return null;

  return {
    id: service.service_id,
    title: service.service_name,
    description: service.description || "",
    tags: Array.isArray(service.keywords) ? service.keywords : [],
    systemExposure: service.system_exposure ?? "open",
    missionImpact: service.service_mission_impact ?? "mission_failure",
    imageUrl,
    ipAddresses: Array.isArray(service.asset?.ip_addresses) ? service.asset.ip_addresses : [],
    countryCode: service.asset?.country_code || "",
    address: service.asset?.address || "",
  };
}

export function buildDependencyRows(
  packages: PTeamPackageVersionSummary[],
  currentServiceId: string,
): SbomDependency[] {
  if (!Array.isArray(packages) || !currentServiceId) return [];

  return packages.map((pkg) => ({
    packageVersionId: pkg.package_version_id,
    serviceId: currentServiceId,
    name: pkg.package_name,
    version: pkg.package_version || "",
    type: pkg.ecosystem,
    license: "",
    ssvcPriority: pkg.ssvc_priority || "no_known_vulnerability",
  }));
}
