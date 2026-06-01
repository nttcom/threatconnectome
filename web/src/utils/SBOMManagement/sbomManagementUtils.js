export const NEW_SBOM_ID = "__new_sbom__";

export function createId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

export function normalizeTags(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

export function getNextActiveIdAfterRemoval(items, removedId) {
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

export function isDeleteConfirmationValid(input, title) {
  return input.trim() === (title || "Untitled SBOM");
}

export function buildServiceTabsFromPTeam(services) {
  if (!Array.isArray(services)) return [];

  return services.map((service) => ({
    id: service.service_id,
    title: service.service_name,
  }));
}

export function buildCurrentServiceFromPTeam(services, currentServiceId, imageUrl = "") {
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
    deployments: (service.asset?.ip_addresses || []).map((ip, index) => ({
      id: `dep-${service.service_id}-${index}`,
      ip,
      location: "",
    })),
  };
}

export function buildDependencyRows(packages, currentServiceId) {
  if (!Array.isArray(packages) || !currentServiceId) return [];

  return packages.map((pkg) => ({
    packageId: pkg.package_id,
    serviceId: currentServiceId,
    name: pkg.package_name,
    version: "",
    type: pkg.ecosystem,
    license: "",
    ssvcPriority: pkg.ssvc_priority || "no_known_vulnerability",
  }));
}
