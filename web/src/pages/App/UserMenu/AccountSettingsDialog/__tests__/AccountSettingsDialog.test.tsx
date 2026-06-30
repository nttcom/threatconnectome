import { render, screen } from "@testing-library/react";
import i18n from "i18next";

import { useAuth } from "../../../../../hooks/auth";
import { AccountSettingsDialog } from "../AccountSettingsDialog";
import enApp from "../../../../../../public/locales/en/app.json";

vi.mock("../../../../../hooks/auth", async (importOriginal) => {
  const actual = (await importOriginal()) as object;
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
  beforeAll(() => {
    i18n.addResourceBundle("en", "app", enApp, true, true);
  });

  beforeEach(() => {
    vi.mocked(useAuth).mockReturnValue({
      isAuthenticatedWithSaml: vi.fn().mockReturnValue(false),
    } as unknown as ReturnType<typeof useAuth>);
  });

  it("renders team names without preserving repeated half-width spaces", () => {
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
          uid: "uid-1",
          disabled: false,
          pteam_roles: [
            {
              is_admin: false,
              pteam: {
                pteam_id: "team-1",
                pteam_name: "Gamma  Delta",
                contact_info: "",
              },
            },
          ],
        }}
      />,
    );

    const teamName = screen
      .getAllByText((_, element) => element?.textContent === "Gamma  Delta")
      .find((element) => element.tagName === "P");
    if (!teamName) {
      throw new Error("Team name paragraph was not found.");
    }
    expect(window.getComputedStyle(teamName).whiteSpace).not.toBe("pre");
  });

  it("shows the lowest experience bucket when user years are below 2", () => {
    render(
      <AccountSettingsDialog
        accountSettingOpen
        setAccountSettingOpen={vi.fn()}
        onUpdateUser={vi.fn()}
        userMe={{
          email: "test@example.com",
          user_id: "user-1",
          years: 1,
          default_pteam_id: null,
          uid: "uid-1",
          disabled: false,
          pteam_roles: [],
        }}
      />,
    );

    expect(screen.getAllByRole("combobox")[0]).toHaveTextContent("0+ year");
  });
});
