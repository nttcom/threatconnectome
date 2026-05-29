import { render, screen } from "@testing-library/react";

import { useAuth } from "../../../../../hooks/auth";
import { AccountSettingsDialog } from "../AccountSettingsDialog";

vi.mock("../../../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

vi.mock("../../DeleteAccountDialog", () => ({
  DeleteAccountDialog: () => null,
}));

vi.mock("../TwoFactorAuthSection/TwoFactorAuthSection", () => ({
  TwoFactorAuthSection: () => null,
}));

describe("AccountSettingsDialog", () => {
  it("renders team names without preserving repeated half-width spaces", () => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticatedWithSaml: vi.fn().mockReturnValue(false),
    });

    render(
      <AccountSettingsDialog
        accountSettingOpen
        setAccountSettingOpen={vi.fn()}
        onUpdateUser={vi.fn()}
        userMe={{
          email: "test@example.com",
          user_id: "user-1",
          years: 0,
          default_pteam_id: null,
          pteam_roles: [
            {
              pteam: {
                pteam_id: "team-1",
                pteam_name: "Gamma  Delta",
              },
            },
          ],
        }}
      />,
    );

    const teamName = screen
      .getAllByText((_, element) => element?.textContent === "Gamma  Delta")
      .find((element) => element.tagName === "P");
    expect(window.getComputedStyle(teamName).whiteSpace).not.toBe("pre");
  });
});
