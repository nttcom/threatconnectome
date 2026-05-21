export const NEW_SBOM_ID = "__new_sbom__";

const licenses = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "EPL-1.0"];

const dependencySeeds = {
  maven: [
    "spring-boot-starter-web",
    "spring-boot-starter-security",
    "postgresql",
    "jackson-databind",
    "logback-classic",
    "hibernate-core",
    "commons-lang3",
    "guava",
    "kafka-clients",
    "junit-jupiter-api",
  ],
  npm: [
    "react",
    "react-dom",
    "vite",
    "typescript",
    "@mui/material",
    "@mui/icons-material",
    "@emotion/react",
    "zod",
    "vitest",
    "msw",
  ],
};

export function createId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

const ssvcPriorityCycle = [
  "immediate",
  "out_of_cycle",
  "scheduled",
  "defer",
  "no_known_vulnerability",
];

export function generateDependencies(count, ecosystem) {
  const names = dependencySeeds[ecosystem] || dependencySeeds.maven;

  return Array.from({ length: count }, (_, index) => {
    const baseName = names[index % names.length];

    return {
      name:
        index < names.length
          ? baseName
          : `${baseName}-module-${Math.floor(index / names.length) + 1}`,
      version: `${ecosystem === "npm" ? 1 + (index % 18) : 2 + (index % 7)}.${(index * 3) % 20}.${(index * 7) % 30}`,
      type: ecosystem,
      license: licenses[index % licenses.length],
      ssvcPriority: ssvcPriorityCycle[index % ssvcPriorityCycle.length],
    };
  });
}

export function parseDependenciesFromSbom(json) {
  const components = Array.isArray(json?.components) ? json.components : [];
  const packages = Array.isArray(json?.packages) ? json.packages : [];

  if (components.length > 0) {
    return components.map((component, index) => ({
      name: component.name || component["bom-ref"] || `component-${index + 1}`,
      version: component.version || "-",
      type: component.type || component.purl?.split(":")?.[0]?.replace("pkg", "") || "component",
      license:
        component.licenses?.[0]?.license?.id ||
        component.licenses?.[0]?.license?.name ||
        component.licenses?.[0]?.expression ||
        "unknown",
    }));
  }

  if (packages.length > 0) {
    return packages.map((pkg, index) => ({
      name: pkg.name || pkg.SPDXID || `package-${index + 1}`,
      version: pkg.versionInfo || pkg.version || "-",
      type: "spdx",
      license: pkg.licenseConcluded || pkg.licenseDeclared || "unknown",
    }));
  }

  return [];
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
      .filter((pkg) => Array.isArray(pkg.service_ids) && pkg.service_ids.includes(service.service_id))
      .map((pkg) => ({
        name: pkg.package_name,
        version: "",
        type: pkg.ecosystem,
        license: "",
        ssvcPriority: pkg.ssvc_priority || "no_known_vulnerability",
      })),
  }));
}

export function createDefaultSboms() {
  return [
    {
      id: "core-api",
      title: "Core API SBOM",
      description:
        "決済・ユーザー管理を担当するCore APIのSBOM。CycloneDX形式のアップロードを想定しています。",
      tags: ["backend", "api", "critical"],
      imageUrl:
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=900&auto=format&fit=crop",
      deployments: [
        { id: "dep-1", ip: "10.24.8.15", location: "Tokyo / prod-a" },
        { id: "dep-2", ip: "10.24.8.16", location: "Tokyo / prod-b" },
      ],
      dependencies: generateDependencies(97, "maven"),
    },
    {
      id: "admin-ui",
      title: "Admin UI SBOM",
      description: "管理画面フロントエンドの依存関係を管理するSBOM。",
      tags: ["frontend", "react"],
      imageUrl:
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=900&auto=format&fit=crop",
      deployments: [{ id: "dep-3", ip: "172.18.0.42", location: "Osaka / staging" }],
      dependencies: generateDependencies(7, "npm"),
    },
  ];
}
