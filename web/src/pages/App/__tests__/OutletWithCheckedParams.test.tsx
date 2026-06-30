import { render, screen, waitFor } from "@testing-library/react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetUserMeQuery } from "../../../services/tcApi";
import { OutletWithCheckedParams } from "../OutletWithCheckedParams";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = (await importOriginal()) as object;
  return {
    ...actual,
    Outlet: () => <main>Checked outlet</main>,
    useLocation: vi.fn(),
    useNavigate: vi.fn(),
  };
});

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = (await importOriginal()) as object;
  return {
    ...actual,
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

vi.mock("../../../services/tcApi", () => ({
  useGetUserMeQuery: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

describe("OutletWithCheckedParams", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useSkipUntilAuthUserIsReady).mockReturnValue(false);
    vi.mocked(useNavigate).mockReturnValue(vi.fn());
    vi.mocked(useLocation).mockReturnValue({
      pathname: "/pteam",
      search: "?pteamId=removed-team",
      hash: "",
      state: null,
      key: "test",
    });
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: {
        user_id: "user-1",
        uid: "uid-1",
        email: "user@example.com",
        disabled: false,
        years: 0,
        default_pteam_id: null,
        pteam_roles: [],
      },
      error: undefined,
      isLoading: false,
      isFetching: false,
    } as unknown as ReturnType<typeof useGetUserMeQuery>);
  });

  it("redirects invalid team URLs before rendering child routes", async () => {
    const navigate = vi.fn();
    vi.mocked(useNavigate).mockReturnValue(navigate);

    render(<OutletWithCheckedParams />);

    expect(screen.queryByText("Checked outlet")).not.toBeInTheDocument();
    await waitFor(() => expect(navigate).toHaveBeenCalledWith("/pteam"));
  });

  it("renders child routes when the current team is valid", () => {
    vi.mocked(useLocation).mockReturnValue({
      pathname: "/pteam",
      search: "?pteamId=team-1",
      hash: "",
      state: null,
      key: "test",
    });
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: {
        user_id: "user-1",
        uid: "uid-1",
        email: "user@example.com",
        disabled: false,
        years: 0,
        default_pteam_id: null,
        pteam_roles: [{ pteam: { pteam_id: "team-1", pteam_name: "Team 1", contact_info: "" } }],
      },
      error: undefined,
      isLoading: false,
      isFetching: false,
    } as unknown as ReturnType<typeof useGetUserMeQuery>);

    render(<OutletWithCheckedParams />);

    expect(screen.getByText("Checked outlet")).toBeInTheDocument();
  });
});
