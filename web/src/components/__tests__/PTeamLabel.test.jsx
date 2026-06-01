import { render, screen } from "@testing-library/react";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { PTeamLabel } from "../PTeamLabel";

vi.mock("../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

vi.mock("../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetUserMeQuery: vi.fn(),
  };
});

vi.mock("../PTeamSettingsModal", () => ({
  PTeamSettingsModal: () => null,
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key) => key,
  }),
}));

describe("PTeamLabel", () => {
  it("renders team name without preserving repeated half-width spaces", () => {
    vi.mocked(useSkipUntilAuthUserIsReady).mockReturnValue(false);
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: {
        pteam_roles: [
          {
            pteam: {
              pteam_id: "team-1",
              pteam_name: "Alpha  Beta",
            },
          },
        ],
      },
      error: undefined,
      isLoading: false,
    });

    render(<PTeamLabel pteamId="team-1" />);

    const label = screen.getByRole("heading", { level: 5 });
    expect(window.getComputedStyle(label).whiteSpace).not.toBe("pre");
  });
});
