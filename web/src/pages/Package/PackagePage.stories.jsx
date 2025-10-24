import { ThemeProvider, createTheme } from "@mui/material/styles";
import { http, HttpResponse } from "msw"; // MSW v2+ のインポート
import React from "react"; // Error Boundary のために React をインポート
import { MemoryRouter, Routes, Route } from "react-router-dom";

import { Package } from "./PackagePage"; // コンポーネントへのパス

// (MUIテーマ、モックデータ定義)
const theme = createTheme();
const pteamId = "pteam-abc-123";
const serviceId = "service-xyz-789";
const packageId = "pkg-uuid-456";
const mockPTeam = {
  pteam_id: pteamId,
  pteam_name: "Example Team",
  services: [{ service_id: serviceId, service_name: "My Production Service" }],
};
const mockDependencies = [
  {
    dependency_id: "dep-1",
    target: "pom.xml",
    package_version: "1.2.3",
    package_name: "log4j",
    package_source_name: "org.apache.logging:log4j-core",
    package_manager: "maven",
    package_ecosystem: "maven",
    vuln_matching_ecosystem: "maven",
  },
  {
    dependency_id: "dep-2",
    target: "another.xml",
    package_version: "1.2.3",
    package_name: "log4j",
    package_source_name: "org.apache.logging:log4j-core",
    package_manager: "maven",
    package_ecosystem: "maven",
  },
];
const mockVulnIdsUnsolved = {
  vuln_ids: ["CVE-2021-44228", "CVE-2022-1234"],
};
const mockVulnIdsSolved = {
  vuln_ids: ["CVE-2020-5678"],
};
const mockTicketCountsUnsolved = {
  ssvc_priority_count: {
    immediate: 1,
    out_of_cycle: 1,
    scheduled: 0,
    defer: 0,
  },
};
const mockTicketCountsSolved = {
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 0,
    scheduled: 1,
    defer: 0,
  },
};
const mockVulnDetails = {
  "CVE-2021-44228": {
    vuln_id: "CVE-2021-44228",
    title: "Log4Shell: RCE in Log4j",
    detail: "A remote code execution vulnerability...",
    cve_id: "CVE-2021-44228",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["2.0.0"],
        fixed_versions: ["2.17.1"],
      },
    ],
  },
  "CVE-2022-1234": {
    vuln_id: "CVE-2022-1234",
    title: "Another Vulnerability",
    cve_id: "CVE-2022-1234",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["1.0.0"],
        fixed_versions: ["1.1.0"],
      },
    ],
  },
  "CVE-2020-5678": {
    vuln_id: "CVE-2020-5678",
    title: "Solved Vulnerability",
    cve_id: "CVE-2020-5678",
    vulnerable_packages: [
      {
        affected_name: "log4j",
        ecosystem: "maven",
        affected_versions: ["0.9.0"],
        fixed_versions: ["0.9.1"],
      },
    ],
  },
};
const mockVulnActions = {
  "CVE-2021-44228": [
    { action_type: "patch", recommended: true, action: "Apply patch provided by vendor." },
  ],
  "CVE-2022-1234": [],
  "CVE-2020-5678": [],
};
const mockTickets = {
  "CVE-2021-44228": [
    {
      ticket_id: "ticket-1",
      dependency_id: "dep-1",
      ssvc_deployer_priority: "immediate",
      ticket_status: {
        ticket_handling_status: "acknowledged",
        scheduled_at: "2025-10-20T12:00:00Z",
        assignees: ["user-1"],
      },
    },
  ],
  "CVE-2022-1234": [
    {
      ticket_id: "ticket-2",
      dependency_id: "dep-1",
      ssvc_deployer_priority: "out_of_cycle",
      ticket_status: {
        ticket_handling_status: "alerted",
        scheduled_at: null,
        assignees: [],
      },
    },
  ],
  "CVE-2020-5678": [
    {
      ticket_id: "ticket-3",
      dependency_id: "dep-2",
      ssvc_deployer_priority: "scheduled",
      ticket_status: {
        ticket_handling_status: "completed",
        scheduled_at: "2025-01-01T00:00:00Z",
        assignees: ["user-1", "user-2"],
      },
    },
  ],
};
const mockMembersList = [
  { user_id: "user-1", name: "Alice", email: "alice@example.com" },
  { user_id: "user-2", name: "Bob", email: "bob@example.com" },
];

// ★★★ 不足していたユーザー情報のモックデータを追加 ★★★
const mockUserMe = {
  user_id: "current-user-123",
  name: "Current User",
  email: "current.user@example.com",
  pteam_roles: [], // 必要であれば追加
};

// MSW v2+ 構文のAPIハンドラ
const successHandlers = [
  // 1. useGetPTeamQuery
  http.get(`*/pteams/${pteamId}`, () => {
    return HttpResponse.json(mockPTeam);
  }),
  // 2. useGetDependenciesQuery
  http.get(`*/pteams/${pteamId}/dependencies`, ({ request }) => {
    const url = new URL(request.url);
    if (
      url.searchParams.get("service_id") === serviceId &&
      url.searchParams.get("package_id") === packageId
    ) {
      return HttpResponse.json(mockDependencies);
    }
  }),
  // 3. useGetPTeamVulnIdsTiedToServicePackageQuery
  http.get(`*/pteams/${pteamId}/vuln_ids`, ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("related_ticket_status") === "unsolved") {
      return HttpResponse.json(mockVulnIdsUnsolved);
    }
    if (url.searchParams.get("related_ticket_status") === "solved") {
      return HttpResponse.json(mockVulnIdsSolved);
    }
  }),
  // 4. useGetPTeamTicketCountsTiedToServicePackageQuery
  http.get(`*/pteams/${pteamId}/ticket_counts`, ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("related_ticket_status") === "unsolved") {
      return HttpResponse.json(mockTicketCountsUnsolved);
    }
    if (url.searchParams.get("related_ticket_status") === "solved") {
      return HttpResponse.json(mockTicketCountsSolved);
    }
  }),
  // 5. useGetVulnQuery
  http.get("*/vulns/:vulnId", ({ params }) => {
    const { vulnId } = params;
    const vulnData = mockVulnDetails[vulnId];
    if (vulnData) {
      return HttpResponse.json(vulnData);
    }
    return HttpResponse.json({ message: "Not Found" }, { status: 404 });
  }),
  // 6. useGetVulnActionsQuery
  http.get("*/vulns/:vulnId/actions", ({ params }) => {
    const { vulnId } = params;
    const actionsData = mockVulnActions[vulnId];
    if (actionsData) {
      return HttpResponse.json(actionsData);
    }
    return HttpResponse.json([]);
  }),
  // 7. useGetPteamTicketsQuery
  http.get(`*/pteams/${pteamId}/tickets`, ({ request }) => {
    const url = new URL(request.url);
    const vulnId = url.searchParams.get("vuln_id");
    const reqPackageId = url.searchParams.get("package_id");
    const reqServiceId = url.searchParams.get("service_id");

    if (reqPackageId === packageId && reqServiceId === serviceId && mockTickets[vulnId]) {
      return HttpResponse.json(mockTickets[vulnId]);
    }
    return HttpResponse.json([]);
  }),
  // 8. useGetPTeamMembersQuery
  http.get(`*/pteams/${pteamId}/members`, () => {
    return HttpResponse.json(mockMembersList);
  }),

  // ★★★ 9. useGetUserMeQuery (NEW - ReportCompletedActions 用) ★★★
  http.get("*/users/me", () => {
    return HttpResponse.json(mockUserMe);
  }),
];

// (ErrorBoundary クラスは変更なし)
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidUpdate(prevProps) {
    if (prevProps.children.key !== this.props.children.key) {
      this.setState({ hasError: false, error: null });
    }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, border: "2px dashed red", color: "red" }}>
          <h2>コンポーネントがエラーをスローしました (これは正常なテストです):</h2>
          <pre>{this.state.error?.message || JSON.stringify(this.state.error)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// (export default, renderStory は変更なし)
export default {
  title: "Package/PackagePage",
  component: Package,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
};

const renderStory = (initialPath) => (
  <ThemeProvider theme={theme}>
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/package/:packageId" element={<Package />} />
      </Routes>
    </MemoryRouter>
  </ThemeProvider>
);

// (Default は変更なし)
export const Default = {
  render: () => renderStory(`/package/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`),
  parameters: {
    msw: {
      handlers: successHandlers, // 9個のハンドラすべてを使用
    },
  },
};

// ★★★ LOADING ストーリーを修正 ★★★
// (slice(1) -> slice(1, 8) or slice(-8) ではなく、明示的にハンドラを指定)
export const Loading = {
  render: () => renderStory(`/package/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`),
  parameters: {
    msw: {
      handlers: [
        // 1. getPTeamQuery: 無限待機
        http.get(`*/pteams/${pteamId}`, async () => {
          await new Promise(() => {});
        }),
        // 2-8. 他の 7 つのハンドラは成功させる
        successHandlers[1], // getDependencies
        successHandlers[2], // getVulnIds (unsolved)
        successHandlers[3], // getTicketCounts (unsolved)
        successHandlers[4], // getVuln
        successHandlers[5], // getVulnActions
        successHandlers[6], // getTickets
        successHandlers[7], // getMembers
        // ★ 9. getUserMe も成功させる
        successHandlers[8], // getUserMe
      ],
    },
  },
};

// ★★★ DEPENDENCIES ERROR ストーリーを修正 ★★★
// (slice(2) -> slice(2, 8) or slice(-7) ではなく、明示的にハンドラを指定)
export const DependenciesError = {
  render: () => renderStory(`/package/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`),
  decorators: [
    (Story, context) => (
      <ErrorBoundary key={JSON.stringify(context.args)}>
        <Story />
      </ErrorBoundary>
    ),
  ],
  parameters: {
    msw: {
      handlers: [
        // 1. getPTeam: 成功
        successHandlers[0],
        // 2. getDependencies: 失敗
        http.get(`*/pteams/${pteamId}/dependencies`, () => {
          return HttpResponse.json({ message: "Internal Server Error" }, { status: 500 });
        }),
        // 3-8. 他の 6 つのハンドラは成功させる
        successHandlers[2], // getVulnIds (unsolved)
        successHandlers[3], // getTicketCounts (unsolved)
        successHandlers[4], // getVuln
        successHandlers[5], // getVulnActions
        successHandlers[6], // getTickets
        successHandlers[7], // getMembers
        // ★ 9. getUserMe も成功させる
        successHandlers[8], // getUserMe
      ],
    },
  },
};

// (NoPTeamId は変更なし)
export const NoPTeamId = {
  render: () => renderStory(`/package/${packageId}?serviceId=${serviceId}`),
};

// ★★★ NoVulnerabilities ストーリーを修正 ★★★
// (slice(-4) ではなく、明示的にハンドラを指定)
export const NoVulnerabilities = {
  render: () => renderStory(`/package/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`),
  parameters: {
    msw: {
      handlers: [
        successHandlers[0], // pteam
        successHandlers[1], // dependencies

        http.get(`*/pteams/${pteamId}/vuln_ids`, () => {
          return HttpResponse.json({ vuln_ids: [] });
        }),
        http.get(`*/pteams/${pteamId}/ticket_counts`, () => {
          return HttpResponse.json({
            ssvc_priority_count: { immediate: 0, out_of_cycle: 0, scheduled: 0, defer: 0 },
          });
        }),

        // vuln, actions, tickets は呼び出されないが、members と userMe は呼び出される
        successHandlers[4], // getVuln (空データ用)
        successHandlers[5], // getVulnActions (空データ用)
        successHandlers[6], // getTickets (空データ用)
        successHandlers[7], // getMembers
        // ★ 9. getUserMe も成功させる
        successHandlers[8], // getUserMe
      ],
    },
  },
};
