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
  { id: "user3", name: "Jiro Sato" },
  { id: "user4", name: "Sachiko Tanaka" },
];

export const mockPackageData = {
  serviceName: "Monolith Service",
  packageName: "log4j-core",
  packageManager: "Maven",
  packageUUID: "a1b2c3d4-e5f6-7890-1234-567890abcdef",
};

export const mockPackageReferences = [
  { target: "webapp/pom.xml", version: "2.14.1", service: "Frontend Service" },
  { target: "backend-api/pom.xml", version: "2.14.1", service: "Backend API" },
  { target: "notification-batch/pom.xml", version: "2.13.0", service: "Notification Batch" },
];

export const mockDefaultSafetyImpact = "Medium";

export const mockSsvcCounts = { immediate: 2, high: 1, medium: 1, low: 0 };

export const mockTabCounts = { unsolved: 4, solved: 42 };
