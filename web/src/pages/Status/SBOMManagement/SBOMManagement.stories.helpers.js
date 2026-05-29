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

const ssvcPriorityCycle = [
  "immediate",
  "out_of_cycle",
  "scheduled",
  "defer",
  "no_known_vulnerability",
];

function generateDependencies(count, ecosystem) {
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
