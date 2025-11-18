import userEvent from "@testing-library/user-event";
import { describe, it, vi } from "vitest";

import { fireEvent, render, screen } from "../../../utils/__tests__/test-utils";
import { Package } from "../PackagePage";

import { setupApiMocks } from "./apiMocks";

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

describe("PackagePage Component Unit Tests", () => {
  it("should render correctly with successful API calls", async () => {
    setupApiMocks();

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
