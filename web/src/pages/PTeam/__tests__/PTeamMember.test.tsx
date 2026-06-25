import { createTheme, ThemeProvider } from "@mui/material";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { Mock } from "vitest";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetPTeamQuery, useGetUserMeQuery } from "../../../services/tcApi";
import { PTeamMember } from "../PTeamMember";
import type { PteamMemberGetResponse, UserResponse } from "../../../../types/types.gen";

vi.mock("../../../hooks/auth", async (importOriginal: () => Promise<object>) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

vi.mock("../../../services/tcApi", async (importOriginal: () => Promise<object>) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetPTeamQuery: vi.fn(),
    useGetUserMeQuery: vi.fn(),
  };
});

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

vi.mock("../InvitationManageDialog", () => ({
  InvitationManageDialog: () => <button type="button">manage invitations</button>,
}));

vi.mock("../PTeamAuthEditor", () => ({
  PTeamAuthEditor: ({ isCurrentUserAdmin }: { isCurrentUserAdmin: boolean }) => (
    <label>
      admin authority
      <input type="checkbox" disabled={!isCurrentUserAdmin} />
    </label>
  ),
}));

vi.mock("../PTeamMemberRemoveModal", () => ({
  PTeamMemberRemoveModal: () => <div>remove member modal</div>,
}));

const pteamId = "pteam-1";
const currentUserId = "user-current";
const theme = createTheme();

const members: Array<PteamMemberGetResponse> = [
  {
    user_id: currentUserId,
    uid: "uid-current",
    email: "current@example.com",
    disabled: false,
    years: 3,
    is_admin: false,
  },
  {
    user_id: "user-member",
    uid: "uid-member",
    email: "member@example.com",
    disabled: false,
    years: 1,
    is_admin: false,
  },
];

type RenderPTeamMemberOptions = {
  userMe?: Partial<UserResponse>;
  memberOverrides?: Record<string, Partial<PteamMemberGetResponse>>;
};

const renderPTeamMember = ({
  userMe = {},
  memberOverrides = {},
}: RenderPTeamMemberOptions = {}) => {
  vi.mocked(useSkipUntilAuthUserIsReady).mockReturnValue(false);
  (useGetUserMeQuery as Mock).mockReturnValue({
    data: {
      user_id: currentUserId,
      uid: "uid-current",
      email: "current@example.com",
      disabled: false,
      years: 3,
      pteam_roles: [],
      default_pteam_id: null,
      ...userMe,
    },
    error: undefined,
    isLoading: false,
    isFetching: false,
  });
  (useGetPTeamQuery as Mock).mockReturnValue({
    data: {
      pteam_id: pteamId,
      pteam_name: "Test PTeam",
    },
    error: undefined,
    isLoading: false,
  });

  const testMembers = members.map((member) => ({
    ...member,
    ...memberOverrides[member.user_id],
  }));

  return render(
    <ThemeProvider theme={theme}>
      <PTeamMember pteamId={pteamId} members={testMembers} />
    </ThemeProvider>,
  );
};

describe("PTeamMember", () => {
  it("renders when userMe pteam roles do not include the current pteam yet", () => {
    renderPTeamMember();

    expect(screen.getByText("current@example.com")).toBeInTheDocument();
    expect(screen.getByText("member@example.com")).toBeInTheDocument();
  });

  it("enables invitation management and member authority actions from the members response admin flag", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const { container } = renderPTeamMember({
      memberOverrides: {
        [currentUserId]: { is_admin: true },
      },
    });

    expect(screen.getByRole("button", { name: "manage invitations" })).toBeInTheDocument();

    const memberMenuButton = container.querySelector("#pteam-member-button-user-member");
    expect(memberMenuButton).not.toBeNull();
    if (!memberMenuButton) throw new Error("member menu button was not found");
    await ue.click(memberMenuButton);

    expect(screen.getByText("removeFromTeam")).toBeInTheDocument();
    await ue.click(screen.getByText("authorities"));

    expect(screen.getByLabelText("admin authority")).toBeEnabled();
  });
});
