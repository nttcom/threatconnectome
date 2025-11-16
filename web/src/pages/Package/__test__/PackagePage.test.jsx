import userEvent from "@testing-library/user-event";
import { describe, it, vi } from "vitest";

import {
  useGetDependenciesQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPteamTicketsQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetUserMeQuery,
  useGetVulnActionsQuery,
  useGetVulnQuery,
} from "../../../services/tcApi";
import { fireEvent, render, screen } from "../../../utils/__tests__/test-utils";
import { Package } from "../PackagePage";

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
  };
});

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
    vi.mocked(useGetDependenciesQuery).mockReturnValue({
      data: MOCK_DEPENDENCIES,
      isLoading: false,
      isSuccess: true,
    });

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
    vi.mocked(useGetPteamTicketsQuery).mockImplementation((args) => {
      const vulnId = args?.vulnId || "unknown";
      return {
        data: [
          {
            ticket_id: `ticket-for-${vulnId}`,
            ssvc_deployer_priority: "Immediate",
            ticket_status: {
              ticket_handling_status: "alerted",
              assignees: [],
            },
          },
        ],
        isLoading: false,
        isSuccess: true,
      };
    });
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: { user_id: "test-user-id" },
      isLoading: false,
      isSuccess: true,
    });

    const packageId = "pkg:npm/react@18.2.0";
    const pteamId = "pteam-abc";
    const serviceId = "svc-xyz";

    const route = `/packages/${encodeURIComponent(packageId)}?pteamId=${pteamId}&serviceId=${serviceId}`;
    const path = "/packages/:packageId";

    render(<Package />, { route, path });

    const selectWrappers = screen.getAllByTestId("safety-impact-select-ticket-for-CVE-2023-0002");

    const selectWrapper = selectWrappers[0];
    const combobox = selectWrapper.querySelector('[role="combobox"]');
    fireEvent.mouseDown(combobox);

    const dialog = await screen.findByRole("dialog");
    expect(dialog).toBeInTheDocument();

    const dialogSelect = await screen.findByTestId("dialog-safety-impact-select");
    const dialogCombobox = dialogSelect.querySelector('[role="combobox"]');
    fireEvent.mouseDown(dialogCombobox);

    const menuItems = await screen.findAllByRole("option");

    const catastrophicOption = menuItems.find((item) => item.textContent.includes("Catastrophic"));
    expect(catastrophicOption).toBeDefined();
    await userEvent.click(catastrophicOption);

    expect(dialogCombobox.textContent).toBe("Catastrophic");

    const saveButton = await screen.findByRole("button", { name: /save/i });
    expect(saveButton).not.toBeDisabled();

    await userEvent.click(saveButton);
  });
});
