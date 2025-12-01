// Mock data for PackagePage stories (PackagePage-specific data only)
// Shared data (VulnDetails, Dependencies, Tickets) are imported from tables/split-view/mocks

export const pteamId = "pteam-abc-123";
export const serviceId = "service-xyz-789";
export const packageId = "pkg-uuid-456";

export const mockPTeam = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  services: [
    { service_id: serviceId, service_name: "My Production Service", service_safety_impact: "high" },
  ],
};

export const mockVulnIdsUnsolved = {
  vuln_ids: ["CVE-2021-44228", "CVE-2022-1234"],
};

export const mockVulnIdsSolved = {
  vuln_ids: ["CVE-2020-5678"],
};

export const mockTicketCountsUnsolved = {
  ssvc_priority_count: {
    immediate: 1,
    out_of_cycle: 1,
    scheduled: 0,
    defer: 0,
  },
};

export const mockTicketCountsSolved = {
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 0,
    scheduled: 1,
    defer: 0,
  },
};

export const mockVulnActions = {
  "CVE-2021-44228": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "CVE-2022-1234": [],
  "CVE-2020-5678": [],
};

export const mockMembersList = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
];

export const mockUserMe = {
  user_id: "current-user-123",
  name: "Current User",
  email: "current.user@example.com",
  pteam_roles: [],
};
