// mockData.js

const longReasonText =
  'This vulnerability is rated as "High" Impact because it affects a critical, internet-facing authentication service. An exploit could lead to unauthorized access to sensitive customer data...';

// --- 脆弱性データ（完全版） ---
export const mockVulnerabilities = [
  {
    id: "vuln-001",
    title: "setuptools: Path Traversal Vulnerability",
    highestSsvc: "high",
    updated_at: "2025-10-21",
    affected_versions: ["1.2.0"],
    patched_versions: ["1.2.1"],
    // --- 脆弱性詳細情報を追加 ---
    cveId: "CVE-2023-12345",
    description:
      "A path traversal vulnerability in setuptools allows an attacker to access arbitrary files on the filesystem by crafting a malicious package.",
    mitigation:
      "Upgrade setuptools to version 65.5.1 or later. As a temporary workaround, sanitize all package names before installation.",
    tasks: [
      {
        ticket_id: "t1-1",
        target: "webapp/frontend/package.json",
        ticket_handling_status: "Schedule", // "Schedule"に変更
        safety_impact: "High",
        safety_impact_change_reason:
          "This component processes user-uploaded files and a path traversal could lead to exposure of sensitive server files.",
        assignees: ["user1", "user2"], // 複数人担当
        due_date: "2025-11-15T23:59:59Z",
        ssvc: "high",
      },
      {
        ticket_id: "t1-2",
        target: "backend/api/requirements.txt",
        ticket_handling_status: "Acknowledge", // "Acknowledge"に変更
        safety_impact: "Medium",
        safety_impact_change_reason: "",
        assignees: [],
        due_date: null,
        ssvc: "medium",
      },
    ],
  },
  {
    id: "vuln-002",
    title: "pypa/setuptools: Remote code execution",
    highestSsvc: "catastrophic",
    updated_at: "2025-10-20",
    affected_versions: ["2.0.0"],
    patched_versions: [],
    cveId: "CVE-2022-54321",
    description:
      "A critical RCE vulnerability exists in the pypa/setuptools library, allowing unauthenticated attackers to execute arbitrary code.",
    mitigation: "Immediate upgrade to the latest version is required. No known workarounds exist.",
    tasks: [
      {
        ticket_id: "t2-1",
        target: "data-processor/pom.xml",
        ticket_handling_status: "Acknowledge",
        safety_impact: "Catastrophic",
        safety_impact_change_reason: "Default impact assessment based on CVSS score.",
        assignees: [],
        due_date: null,
        ssvc: "immediate",
      },
    ],
  },
  {
    id: "vuln-003",
    title: "Log4j: Remote Code Execution (Log4Shell)",
    highestSsvc: "catastrophic",
    updated_at: "2025-10-19",
    affected_versions: ["2.14.1"],
    patched_versions: ["2.15.0", "2.16.0"],
    cveId: "CVE-2021-44228",
    description:
      "Apache Log4j2 <=2.14.1 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
    mitigation:
      "Upgrade to Log4j 2.17.1 or later. Alternatively, set the system property `log4j2.formatMsgNoLookups` to `true`.",
    tasks: [
      {
        ticket_id: "t3-1",
        target: "legacy-system/WEB-INF/lib/log4j-core-2.14.1.jar",
        ticket_handling_status: "Complete", // "Complete"に変更
        safety_impact: "Catastrophic",
        safety_impact_change_reason: longReasonText,
        assignees: ["user3"],
        due_date: "2025-10-25T12:00:00Z",
        ssvc: "immediate",
      },
    ],
  },
];

// --- その他のモックデータ ---

export const mockMembers = [
  { id: "user1", name: "Taro Yamada" },
  { id: "user2", name: "Hanako Suzuki" },
  { id: "user3", name: "John Doe" },
];

export const mockPackageData = {
  serviceName: "Frontend WebApp",
  packageName: "react",
  packageManager: "npm",
  packageUUID: "pkg:npm/react@18.2.0",
};

export const mockPackageReferences = [
  { target: "webapp-main", version: "1.2.3", service: "Service A" },
  { target: "webapp-sub", version: "4.5.6", service: "Service B" },
];

export const mockDefaultSafetyImpact = "High";

export const mockSsvcCounts = {
  immediate: 1,
  "out-of-cycle": 2,
  scheduled: 5,
  defer: 3,
};

export const mockTabCounts = {
  unsolved: 11,
  solved: 42,
};

export const mockPTeam = {
  pteam_id: "pteam-sample-id-for-storybook",
  pteam_name: "Storybook PTeam",
  services: [
    { service_id: "service-a", service_name: "Service Alpha", service_safety_impact: "Medium" },
    { service_id: "service-b", service_name: "Service Bravo", service_safety_impact: "High" },
  ],
};

export const mockDependencies = [
  {
    dependency_id: "dep-001",
    service_id: "service-a",
    package_version_id: "pkg-ver-001",
    package_id: "pkg-uuid-456",
    package_manager: "npm",
    target: "webapp-main",
    dependency_mission_impact: "High",
    package_name: "setuptools",
    package_source_name: "npmjs",
    package_version: "1.2.3",
    package_ecosystem: "npm",
    vuln_matching_ecosystem: "npm",
  },
  {
    dependency_id: "dep-002",
    service_id: "service-b",
    package_version_id: "pkg-ver-002",
    package_id: "pkg-uuid-456",
    package_manager: "npm",
    target: "webapp-sub",
    dependency_mission_impact: "Medium",
    package_name: "setuptools",
    package_source_name: "npmjs",
    package_version: "4.5.6",
    package_ecosystem: "npm",
    vuln_matching_ecosystem: "npm",
  },
];

// --- Vuln IDs (Unsolved) ---
export const mockVulnIdsUnsolved = {
  pteam_id: "pteam-abc-123",
  service_id: "service-a",
  package_id: "pkg-uuid-456",
  related_ticket_status: "unsolved",
  vuln_ids: ["vuln-001", "vuln-002"],
};

// --- Vuln IDs (Solved) ---
export const mockVulnIdsSolved = {
  pteam_id: "pteam-abc-123",
  service_id: "service-a",
  package_id: "pkg-uuid-456",
  related_ticket_status: "solved",
  vuln_ids: ["vuln-003"],
};

// --- Vuln Details Map (API Response Format) ---
export const mockVulnDetails = {
  "vuln-001": {
    title: "setuptools: Path Traversal Vulnerability",
    cve_id: "CVE-2023-12345",
    detail:
      "A path traversal vulnerability in setuptools allows an attacker to access arbitrary files on the filesystem by crafting a malicious package.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 7.5,
    vulnerable_packages: [
      {
        ecosystem: "npm",
        affected_name: "setuptools",
        affected_versions: ["1.2.0", "1.1.9"],
        fixed_versions: ["1.2.1"],
      },
    ],
    vuln_id: "vuln-001",
    created_at: "2025-10-01T00:00:00Z",
    updated_at: "2025-10-21T00:00:00Z",
    created_by: "user-001",
  },
  "vuln-002": {
    title: "pypa/setuptools: Remote code execution",
    cve_id: "CVE-2022-54321",
    detail:
      "A critical RCE vulnerability exists in the pypa/setuptools library, allowing unauthenticated attackers to execute arbitrary code.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 9.8,
    vulnerable_packages: [
      {
        ecosystem: "npm",
        affected_name: "setuptools",
        affected_versions: ["2.0.0", "1.9.9"],
        fixed_versions: ["2.1.0"],
      },
    ],
    vuln_id: "vuln-002",
    created_at: "2025-09-15T00:00:00Z",
    updated_at: "2025-10-20T00:00:00Z",
    created_by: "user-002",
  },
  "vuln-003": {
    title: "Log4j: Remote Code Execution (Log4Shell)",
    cve_id: "CVE-2021-44228",
    detail:
      "Apache Log4j2 <=2.14.1 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 10.0,
    vulnerable_packages: [
      {
        ecosystem: "npm",
        affected_name: "log4j",
        affected_versions: ["2.14.1", "2.14.0"],
        fixed_versions: ["2.15.0", "2.16.0"],
      },
    ],
    vuln_id: "vuln-003",
    created_at: "2025-08-01T00:00:00Z",
    updated_at: "2025-10-19T00:00:00Z",
    created_by: "user-003",
  },
};
