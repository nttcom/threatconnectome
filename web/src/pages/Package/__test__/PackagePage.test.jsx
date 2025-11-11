import { describe, expect, it, vi } from "vitest";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useCreateActionLogMutation,
  useGetDependenciesQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPteamTicketsQuery,
  useGetUserMeQuery,
  useGetVulnActionsQuery,
  useGetVulnQuery,
  useUpdateTicketMutation,
} from "../../../services/tcApi";
import { render, screen } from "../../../utils/__tests__/test-utils";
import { Package } from "../PackagePage";

// 1. 依存関係のモック化
vi.mock("../../../hooks/auth");

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetPTeamQuery: vi.fn(),
    useGetDependenciesQuery: vi.fn(),
    useGetPTeamVulnIdsTiedToServicePackageQuery: vi.fn(),
    useGetPTeamTicketCountsTiedToServicePackageQuery: vi.fn(),
    useGetPTeamMembersQuery: vi.fn(),
    useGetVulnQuery: vi.fn(),
    useGetVulnActionsQuery: vi.fn(),
    useGetPteamTicketsQuery: vi.fn(),
    useGetUserMeQuery: vi.fn(),
    useCreateActionLogMutation: vi.fn(),
    useUpdateTicketMutation: vi.fn(),
  };
});

// 2. モックデータの定義
const MOCK_PTEAM = {
  pteam_id: "pteam-abc",
  pteam_name: "PTeam Alpha",
  services: [{ service_id: "svc-xyz", service_name: "Test Service" }],
  tags: [],
};
const MOCK_DEPENDENCIES = [
  {
    dependency_id: "dep-123",
    target: "target-file.txt",
    package_name: "react",
    package_version: "18.2.0",
    package_source_name: "npm",
    package_manager: "npm",
    package_ecosystem: "npm",
    vuln_matching_ecosystem: "npm",
  },
];
const MOCK_VULN_IDS_SOLVED = { vuln_ids: ["CVE-2023-0001"] };
const MOCK_VULN_IDS_UNSOLVED = { vuln_ids: ["CVE-2023-0002", "CVE-2023-0003"] };
const MOCK_TICKET_COUNTS_SOLVED = { ssvc_priority_count: [{ priority: "high", count: 1 }] };
const MOCK_TICKET_COUNTS_UNSOLVED = { ssvc_priority_count: [{ priority: "critical", count: 2 }] };

describe("PackagePage Component Unit Tests", () => {
  it("should render correctly with successful API calls", async () => {
    // 3. モックの戻り値を設定
    vi.mocked(useSkipUntilAuthUserIsReady).mockReturnValue(false);

    // PackagePageとVulnTableRowViewの両方で使われるフック
    vi.mocked(useGetDependenciesQuery).mockReturnValue({
      data: MOCK_DEPENDENCIES,
      isLoading: false,
      isSuccess: true,
    });

    // PackagePageのフック設定
    vi.mocked(useGetPTeamQuery).mockReturnValue({
      data: MOCK_PTEAM,
      isLoading: false,
      isSuccess: true,
    });
    vi.mocked(useGetPTeamVulnIdsTiedToServicePackageQuery).mockImplementation((args) => {
      if (args.relatedTicketStatus === "solved") {
        return { data: MOCK_VULN_IDS_SOLVED, isLoading: false, isSuccess: true };
      }
      return { data: MOCK_VULN_IDS_UNSOLVED, isLoading: false, isSuccess: true };
    });
    vi.mocked(useGetPTeamTicketCountsTiedToServicePackageQuery).mockImplementation((args) => {
      if (args.relatedTicketStatus === "solved") {
        return { data: MOCK_TICKET_COUNTS_SOLVED, isLoading: false, isSuccess: true };
      }
      return { data: MOCK_TICKET_COUNTS_UNSOLVED, isLoading: false, isSuccess: true };
    });

    // 子コンポーネント群が使うフックの設定
    vi.mocked(useGetPTeamMembersQuery).mockReturnValue({
      data: [],
      isLoading: false,
      isSuccess: true,
    });
    vi.mocked(useGetVulnQuery).mockImplementation(({ vulnId }) => ({
      data: {
        vulnerability_id: vulnId,
        title: `Vulnerability ${vulnId}`,
        updated_at: "2023-10-27T10:00:00.000Z",
        vulnerable_packages: [
          {
            affected_name: "react",
            ecosystem: "npm",
            affected_versions: ["18.2.0"],
            fixed_versions: ["18.2.1"],
          },
        ],
      },
      isLoading: false,
      isSuccess: true,
    }));
    vi.mocked(useGetVulnActionsQuery).mockReturnValue({
      data: [],
      isLoading: false,
      isSuccess: true,
    });
    vi.mocked(useGetPteamTicketsQuery).mockImplementation(() => ({
      data: [
        {
          ticket_id: "ticket-1",
          ssvc_deployer_priority: "Immediate",
          ticket_status: {
            ticket_handling_status: "alerted",
            assignees: [],
          },
        },
      ],
      isLoading: false,
      isSuccess: true,
    }));
    // ReportCompletedActionsが使うフックをモック
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: { user_id: "test-user-id" },
      isLoading: false,
      isSuccess: true,
    });
    vi.mocked(useCreateActionLogMutation).mockReturnValue([
      vi.fn().mockResolvedValue({ logging_id: "log-1" }),
    ]);
    vi.mocked(useUpdateTicketMutation).mockReturnValue([
      vi.fn().mockResolvedValue({ ticket_id: "ticket-1" }),
    ]);

    // 4. コンポーネントの描画
    const packageId = "pkg:npm/react@18.2.0";
    const pteamId = "pteam-abc";
    const serviceId = "svc-xyz";

    const route = `/packages/${encodeURIComponent(packageId)}?pteamId=${pteamId}&serviceId=${serviceId}`;
    const path = "/packages/:packageId";

    render(<Package />, { route, path });

    // 5. アサーション
    // "Test Service" は Chip と Table 内の2箇所に表示されるため、複数見つかるのが正しい挙動
    // そのため、findAllByText を使って要素が1つ以上存在することを確認する
    expect((await screen.findAllByText("Test Service"))[0]).toBeInTheDocument();
    expect(screen.getByText("react")).toBeInTheDocument();
    expect(screen.getByText("npm")).toBeInTheDocument();
    expect(screen.getByText(packageId)).toBeInTheDocument();
    expect(screen.getByText("UNSOLVED VULNS (2)")).toBeInTheDocument();
    expect(screen.getByText("SOLVED VULNS (1)")).toBeInTheDocument();
  });
});
