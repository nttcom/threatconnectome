import {
  PTeamInfo,
  DependencyResponse,
  ServicePackageVulnsSolvedUnsolved,
  ServicePackageTicketCountsSolvedUnsolved,
  VulnResponse,
  TicketResponse,
  UserResponse,
} from "../../../../types/types.gen";
// === Common ID Constants ===
export const pteamId = "pteam-abc-123";
export const serviceId = "service-xyz-789";
export const packageId = "pkg-uuid-456";
// === Common Mock Data ===
export const mockPTeam: PTeamInfo = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  contact_info: "",
  alert_slack: {
    enable: false,
    webhook_url: "",
  },
  alert_ssvc_priority: "immediate",
  alert_mail: {
    enable: false,
    address: "",
  },
  services: [
    {
      service_id: serviceId,
      service_name: "My Production Service",
      service_safety_impact: "negligible",
      service_mission_impact: "mission_failure", // Added default
      system_exposure: "open", // Added default
      description: "", // Added default
      keywords: [], // Added default
    },
  ],
};
export const mockDependencies: DependencyResponse[] = [
  {
    dependency_id: "dep-1",
    service_id: serviceId, // Added default
    package_version_id: "pkg-ver-1", // Added default
    package_id: "pkg-1", // Added default
    target: "pom.xml",
    package_version: "2.14.1",
    package_name: "log4j-core",
    package_source_name: "org.apache.logging.log4j:log4j-core",
    package_manager: "maven",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-2",
    service_id: serviceId, // Added default
    package_version_id: "pkg-ver-2", // Added default
    package_id: "pkg-2", // Added default
    target: "build.gradle",
    package_version: "2.14.1",
    package_name: "log4j-core",
    package_source_name: "org.apache.logging.log4j:log4j-core",
    package_manager: "gradle",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-3",
    service_id: serviceId, // Added default
    package_version_id: "pkg-ver-3", // Added default
    package_id: "pkg-3", // Added default
    target: "settings.gradle",
    package_version: "2.14.0",
    package_name: "log4j-core",
    package_source_name: "org.apache.logging.log4j:log4j-core",
    package_manager: "gradle",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-4",
    service_id: serviceId, // Added default
    package_version_id: "pkg-ver-4", // Added default
    package_id: "pkg-4", // Added default
    target: "ivy.xml",
    package_version: "2.14.1",
    package_name: "log4j-core",
    package_source_name: "org.apache.logging.log4j:log4j-core",
    package_manager: "ivy",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-5",
    service_id: serviceId, // Added default
    package_version_id: "pkg-ver-5", // Added default
    package_id: "pkg-5", // Added default
    target: "libs.versions.toml",
    package_version: "2.14.1",
    package_name: "log4j-core",
    package_source_name: "org.apache.logging.log4j:log4j-core",
    package_manager: "gradle",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
];
export const mockVulnIdsUnsolved: ServicePackageVulnsSolvedUnsolved = {
  pteam_id: pteamId,
  service_id: serviceId,
  package_id: packageId,
  related_ticket_status: "unsolved",
  vuln_ids: ["vuln-001", "vuln-002", "vuln-004", "vuln-005"],
};
export const mockVulnIdsSolved: ServicePackageVulnsSolvedUnsolved = {
  pteam_id: pteamId,
  service_id: serviceId,
  package_id: packageId,
  related_ticket_status: "solved",
  vuln_ids: ["vuln-003"],
};
export const mockTicketCountsUnsolved: ServicePackageTicketCountsSolvedUnsolved = {
  // vuln-001: immediate(2), out_of_cycle(1), scheduled(1), defer(1)
  // vuln-002: immediate(2), out_of_cycle(1), scheduled(1), defer(1)
  pteam_id: pteamId,
  service_id: serviceId,
  package_id: packageId,
  related_ticket_status: "unsolved",
  ssvc_priority_count: {
    immediate: 4,
    out_of_cycle: 2,
    scheduled: 2,
    defer: 2,
  },
};
export const mockTicketCountsSolved: ServicePackageTicketCountsSolvedUnsolved = {
  // vuln-003: immediate(2), out_of_cycle(1), scheduled(1), defer(1)
  pteam_id: pteamId,
  service_id: serviceId,
  package_id: packageId,
  related_ticket_status: "solved",
  ssvc_priority_count: {
    immediate: 2,
    out_of_cycle: 1,
    scheduled: 1,
    defer: 1,
  },
};
export const mockVulnDetails: Record<string, VulnResponse> = {
  "vuln-001": {
    vuln_id: "vuln-001",
    title: "Log4j: Denial of Service via Recursive Lookup",
    cve_id: "CVE-2021-45105",
    detail:
      "Apache Log4j2 versions 2.0-alpha1 through 2.16.0 did not protect from uncontrolled recursion from self-referential lookups, resulting in a StackOverflowError that will terminate the process.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 7.5,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j-core",
        affected_versions: ["2.14.1", "2.14.0", "2.13.3"],
        fixed_versions: ["2.17.0"],
      },
    ],
    created_at: "2025-10-01T00:00:00Z",
    updated_at: "2025-10-21T00:00:00Z",
    created_by: "user-001",
  },
  "vuln-002": {
    vuln_id: "vuln-002",
    title: "Log4j: Remote Code Execution via JDBC Appender",
    cve_id: "CVE-2021-44832",
    detail:
      "Apache Log4j2 versions 2.0-beta7 through 2.17.0 are vulnerable to a remote code execution attack where an attacker with permission to modify the logging configuration file can construct a malicious configuration using a JDBC Appender.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 6.6,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j-core",
        affected_versions: ["2.17.0", "2.16.0", "2.15.0"],
        fixed_versions: ["2.17.1"],
      },
    ],
    created_at: "2025-09-15T00:00:00Z",
    updated_at: "2025-10-20T00:00:00Z",
    created_by: "user-002",
  },
  "vuln-003": {
    vuln_id: "vuln-003",
    title: "Log4j: Remote Code Execution (Log4Shell)",
    cve_id: "CVE-2021-44228",
    detail:
      "Apache Log4j2 <=2.14.1 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
    exploitation: "active",
    automatable: "yes",
    cvss_v3_score: 10.0,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j-core",
        affected_versions: ["2.14.1", "2.14.0"],
        fixed_versions: ["2.15.0", "2.16.0"],
      },
    ],
    created_at: "2025-08-01T00:00:00Z",
    updated_at: "2025-10-19T00:00:00Z",
    created_by: "user-003",
  },
  "vuln-004": {
    vuln_id: "vuln-004",
    title: "Low Severity Information Disclosure",
    cve_id: "CVE-2021-99999",
    detail:
      "A low severity vulnerability that may allow limited information disclosure under specific conditions.",
    exploitation: "none",
    automatable: "no",
    cvss_v3_score: 2.5,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j-core",
        affected_versions: ["2.14.1"],
        fixed_versions: ["2.14.2"],
      },
    ],
    created_at: "2025-07-01T00:00:00Z",
    updated_at: "2025-10-15T00:00:00Z",
    created_by: "user-004",
  },
  "vuln-005": {
    vuln_id: "vuln-005",
    title: "Unscored Vulnerability (Pending Analysis)",
    cve_id: "CVE-2021-00000",
    detail: "This vulnerability is pending CVSS analysis and has not yet been scored.",
    exploitation: "none",
    automatable: "no",
    cvss_v3_score: null,
    vulnerable_packages: [
      {
        ecosystem: "maven",
        affected_name: "log4j-core",
        affected_versions: ["2.14.1"],
        fixed_versions: ["2.15.0"],
      },
    ],
    created_at: "2025-06-01T00:00:00Z",
    updated_at: "2025-10-10T00:00:00Z",
    created_by: "user-005",
  },
};
export type VulnAction = {
  action_type: string;
  recommended: boolean;
  action: string;
};
export const mockVulnActions: Record<string, VulnAction[]> = {
  "vuln-001": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "vuln-002": [],
  "vuln-003": [],
  "vuln-004": [],
  "vuln-005": [],
};
export type Member = {
  user_id: string;
  name: string;
  email: string;
};
export const mockMembersList: Member[] = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
  { user_id: "user-003", name: "Charlie", email: "charlie@example.com" },
];
export const mockUserMe: UserResponse = {
  user_id: "current-user-123",
  uid: "current-user",
  // name: "Current User", // UserResponse does not have name
  email: "current.user@example.com",
  disabled: false,
  years: 5,
  pteam_roles: [],
  default_pteam_id: null,
};
// --- Tickets Data (vuln-001) ---
export const mockTicketsVuln001: TicketResponse[] = [
  {
    ticket_id: "ticket-100",
    vuln_id: "vuln-001",
    dependency_id: "dep-1",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: "catastrophic",
    ticket_safety_impact_change_reason: "Critical vulnerability in dep-1",
    ticket_status: {
      status_id: "status-100",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-25T16:51:50.032Z",
      updated_at: "2025-11-25T16:51:50.032Z",
      assignees: [],
      note: "Initial alert - 未着手",
      scheduled_at: null,
      action_logs: [],
      // current_safety_impact: "catastrophic", // not in TicketStatusResponse
    },
  },
  {
    ticket_id: "ticket-101",
    vuln_id: "vuln-001",
    dependency_id: "dep-2",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "out_of_cycle",
    ticket_safety_impact: "critical",
    ticket_safety_impact_change_reason: "Under investigation",
    ticket_status: {
      status_id: "status-101",
      ticket_handling_status: "acknowledged",
      user_id: "user-002",
      created_at: "2025-11-26T08:00:00.032Z",
      updated_at: "2025-11-26T09:00:00.032Z",
      assignees: ["user-003"],
      note: "Acknowledged - 対応中",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-102",
    vuln_id: "vuln-001",
    dependency_id: "dep-3",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "scheduled",
    ticket_safety_impact: "marginal",
    ticket_safety_impact_change_reason: "Low priority issue",
    ticket_status: {
      status_id: "status-102",
      ticket_handling_status: "scheduled",
      user_id: "user-001",
      created_at: "2025-11-27T10:00:00.032Z",
      updated_at: "2025-11-27T10:00:00.032Z",
      assignees: [],
      note: "Scheduled for next sprint",
      scheduled_at: "2025-12-01T00:00:00.032Z",
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-103",
    vuln_id: "vuln-001",
    dependency_id: "dep-4",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "defer",
    ticket_safety_impact: "negligible",
    ticket_safety_impact_change_reason: "Minimal impact",
    ticket_status: {
      status_id: "status-103",
      ticket_handling_status: "completed",
      user_id: "user-003",
      created_at: "2025-11-20T08:00:00.032Z",
      updated_at: "2025-11-24T08:00:00.032Z",
      assignees: [],
      note: "Completed - resolved",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-104",
    vuln_id: "vuln-001",
    dependency_id: "dep-5",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: null,
    ticket_safety_impact_change_reason: null,
    ticket_status: {
      status_id: "status-104",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-28T10:00:00.032Z",
      updated_at: "2025-11-28T10:00:00.032Z",
      assignees: [],
      note: "Using default safety impact",
      scheduled_at: null,
      action_logs: [],
    },
  },
];
// --- Tickets Data (vuln-002) ---
export const mockTicketsVuln002: TicketResponse[] = [
  {
    ticket_id: "ticket-200",
    vuln_id: "vuln-002",
    dependency_id: "dep-1",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: "catastrophic",
    ticket_safety_impact_change_reason: "Critical vulnerability in dep-1",
    ticket_status: {
      status_id: "status-200",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-25T16:51:50.032Z",
      updated_at: "2025-11-25T16:51:50.032Z",
      assignees: [],
      note: "Initial alert",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-201",
    vuln_id: "vuln-002",
    dependency_id: "dep-2",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "out_of_cycle",
    ticket_safety_impact: "critical",
    ticket_safety_impact_change_reason: "Under investigation",
    ticket_status: {
      status_id: "status-201",
      ticket_handling_status: "acknowledged",
      user_id: "user-002",
      created_at: "2025-11-26T08:00:00.032Z",
      updated_at: "2025-11-26T09:00:00.032Z",
      assignees: ["user-003"],
      note: "Acknowledged",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-202",
    vuln_id: "vuln-002",
    dependency_id: "dep-3",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "scheduled",
    ticket_safety_impact: "marginal",
    ticket_safety_impact_change_reason: "Low priority",
    ticket_status: {
      status_id: "status-202",
      ticket_handling_status: "scheduled",
      user_id: "user-001",
      created_at: "2025-11-27T10:00:00.032Z",
      updated_at: "2025-11-27T10:00:00.032Z",
      assignees: [],
      note: "Scheduled",
      scheduled_at: "2025-12-01T00:00:00.032Z",
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-203",
    vuln_id: "vuln-002",
    dependency_id: "dep-4",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "defer",
    ticket_safety_impact: "negligible",
    ticket_safety_impact_change_reason: "Minimal impact",
    ticket_status: {
      status_id: "status-203",
      ticket_handling_status: "completed",
      user_id: "user-003",
      created_at: "2025-11-20T08:00:00.032Z",
      updated_at: "2025-11-24T08:00:00.032Z",
      assignees: [],
      note: "Completed",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-204",
    vuln_id: "vuln-002",
    dependency_id: "dep-5",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: null,
    ticket_safety_impact_change_reason: null,
    ticket_status: {
      status_id: "status-204",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-28T10:00:00.032Z",
      updated_at: "2025-11-28T10:00:00.032Z",
      assignees: [],
      note: "Using default safety impact",
      scheduled_at: null,
      action_logs: [],
    },
  },
];
// --- Tickets Data (vuln-003) ---
export const mockTicketsVuln003: TicketResponse[] = [
  {
    ticket_id: "ticket-300",
    vuln_id: "vuln-003",
    dependency_id: "dep-1",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: "catastrophic",
    ticket_safety_impact_change_reason: "Critical vulnerability",
    ticket_status: {
      status_id: "status-300",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-25T16:51:50.032Z",
      updated_at: "2025-11-25T16:51:50.032Z",
      assignees: [],
      note: "Initial alert",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-301",
    vuln_id: "vuln-003",
    dependency_id: "dep-2",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "out_of_cycle",
    ticket_safety_impact: "critical",
    ticket_safety_impact_change_reason: "Under investigation",
    ticket_status: {
      status_id: "status-301",
      ticket_handling_status: "acknowledged",
      user_id: "user-002",
      created_at: "2025-11-26T08:00:00.032Z",
      updated_at: "2025-11-26T09:00:00.032Z",
      assignees: ["user-003"],
      note: "Acknowledged",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-302",
    vuln_id: "vuln-003",
    dependency_id: "dep-3",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "scheduled",
    ticket_safety_impact: "marginal",
    ticket_safety_impact_change_reason: "Low priority",
    ticket_status: {
      status_id: "status-302",
      ticket_handling_status: "scheduled",
      user_id: "user-001",
      created_at: "2025-11-27T10:00:00.032Z",
      updated_at: "2025-11-27T10:00:00.032Z",
      assignees: [],
      note: "Scheduled",
      scheduled_at: "2025-12-01T00:00:00.032Z",
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-303",
    vuln_id: "vuln-003",
    dependency_id: "dep-4",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "defer",
    ticket_safety_impact: "negligible",
    ticket_safety_impact_change_reason: "Minimal impact",
    ticket_status: {
      status_id: "status-303",
      ticket_handling_status: "completed",
      user_id: "user-003",
      created_at: "2025-11-20T08:00:00.032Z",
      updated_at: "2025-11-24T08:00:00.032Z",
      assignees: [],
      note: "Completed",
      scheduled_at: null,
      action_logs: [],
    },
  },
  {
    ticket_id: "ticket-304",
    vuln_id: "vuln-003",
    dependency_id: "dep-5",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "immediate",
    ticket_safety_impact: null,
    ticket_safety_impact_change_reason: null,
    ticket_status: {
      status_id: "status-304",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-28T10:00:00.032Z",
      updated_at: "2025-11-28T10:00:00.032Z",
      assignees: [],
      note: "Using default safety impact",
      scheduled_at: null,
      action_logs: [],
    },
  },
];

// --- Tickets Data (vuln-004: Low severity) ---
export const mockTicketsVuln004: TicketResponse[] = [
  {
    ticket_id: "ticket-400",
    vuln_id: "vuln-004",
    dependency_id: "dep-1",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "defer",
    ticket_safety_impact: "negligible",
    ticket_safety_impact_change_reason: "Low severity issue",
    ticket_status: {
      status_id: "status-400",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-25T16:51:50.032Z",
      updated_at: "2025-11-25T16:51:50.032Z",
      assignees: [],
      note: "Low priority - defer",
      scheduled_at: null,
      action_logs: [],
    },
  },
];

// --- Tickets Data (vuln-005: None/Unscored) ---
export const mockTicketsVuln005: TicketResponse[] = [
  {
    ticket_id: "ticket-500",
    vuln_id: "vuln-005",
    dependency_id: "dep-1",
    service_id: serviceId,
    pteam_id: pteamId,
    ssvc_deployer_priority: "defer",
    ticket_safety_impact: "negligible",
    ticket_safety_impact_change_reason: "Pending CVSS analysis",
    ticket_status: {
      status_id: "status-500",
      ticket_handling_status: "alerted",
      user_id: "user-001",
      created_at: "2025-11-25T16:51:50.032Z",
      updated_at: "2025-11-25T16:51:50.032Z",
      assignees: [],
      note: "Awaiting CVSS score",
      scheduled_at: null,
      action_logs: [],
    },
  },
];
