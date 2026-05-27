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

export function buildSbomsFromPTeam(services, packages) {
  if (!Array.isArray(services)) return [];
  const allPackages = Array.isArray(packages) ? packages : [];

  return services.map((service) => ({
    id: service.service_id,
    title: service.service_name,
    description: service.description || "",
    tags: Array.isArray(service.keywords) ? service.keywords : [],
    imageUrl: "",
    deployments: (service.asset?.ip_addresses || []).map((ip, index) => ({
      id: `dep-${service.service_id}-${index}`,
      ip,
      location: "",
    })),
    dependencies: allPackages
      .filter(
        (pkg) => Array.isArray(pkg.service_ids) && pkg.service_ids.includes(service.service_id),
      )
      .map((pkg) => ({
        packageId: pkg.package_id,
        serviceId: service.service_id,
        name: pkg.package_name,
        version: "",
        type: pkg.ecosystem,
        license: "",
        ssvcPriority: pkg.ssvc_priority || "no_known_vulnerability",
      })),
  }));
}
