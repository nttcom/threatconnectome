/* eslint-disable react/prop-types */

import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import i18n from "i18next";
import { I18nextProvider, initReactI18next } from "react-i18next";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import appEn from "../../../../public/locales/en/app.json";
import { useAuth, useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { tcApi, useGetUserMeQuery } from "../../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../../slices/auth";
import { Topbar } from "../Topbar";

// eslint-disable-next-line import/no-named-as-default-member
i18n.use(initReactI18next).init({
  lng: "en",
  fallbackLng: "en",
  ns: ["app"],
  defaultNS: "app",
  resources: {
    en: {
      app: appEn,
    },
  },
  interpolation: {
    escapeValue: false,
  },
});

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useLocation: vi.fn(),
    useNavigate: vi.fn(),
  };
});

vi.mock("react-redux", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useDispatch: vi.fn(),
  };
});

vi.mock("../../../components/LanguageSwitcher", () => ({
  LanguageSwitcher: () => <button type="button">en</button>,
}));

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

vi.mock("../../../services/tcApi", () => ({
  tcApi: {
    util: {
      resetApiState: vi.fn(() => ({ type: "tcApi/resetApiState" })),
    },
  },
  useGetUserMeQuery: vi.fn(),
}));

vi.mock("../PTeamCreateModal", () => ({
  PTeamCreateModal: ({ open }) => (open ? <div role="dialog">Create Team Modal</div> : null),
}));

vi.mock("../UserMenu/AccountSettings", () => ({
  AccountSettings: ({ accountSettingOpen }) =>
    accountSettingOpen ? <div role="dialog">Account Settings Modal</div> : null,
}));

const mockUserMe = {
  user_id: "user-1",
  email: "admin@threatconnectome.example",
  default_pteam_id: "pteam-security",
  pteam_roles: [
    {
      pteam: {
        pteam_id: "pteam-platform",
        pteam_name: "Platform Team",
      },
    },
    {
      pteam: {
        pteam_id: "pteam-security",
        pteam_name: "Security Team",
      },
    },
  ],
};

function renderTopbar({ pathname = "/", search = "?pteamId=pteam-security&serviceId=svc-1" } = {}) {
  vi.mocked(useLocation).mockReturnValue({ pathname, search });
  render(
    <I18nextProvider i18n={i18n}>
      <Topbar />
    </I18nextProvider>,
  );
}

describe("Topbar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(vi.fn());
    vi.mocked(useDispatch).mockReturnValue(vi.fn());
    vi.mocked(useAuth).mockReturnValue({ signOut: vi.fn() });
    vi.mocked(useSkipUntilAuthUserIsReady).mockReturnValue(false);
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: mockUserMe,
      error: null,
      isLoading: false,
    });
  });

  it("renders the topbar controls with localized labels", () => {
    renderTopbar();

    expect(screen.getAllByLabelText("Threatconnectome home")[0]).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Page menu" })[0]).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Team menu" })[0]).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "User menu" })[0]).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "en" })[0]).toBeInTheDocument();
    expect(screen.queryByText(mockUserMe.email)).not.toBeInTheDocument();
  });

  it("keeps the topbar available without throwing when user info loading fails", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: undefined,
      error: { status: 500 },
      isLoading: false,
    });

    renderTopbar();

    expect(screen.queryByText("Something went wrong")).not.toBeInTheDocument();
    screen.getAllByRole("button", { name: "Team menu" }).forEach((button) => {
      expect(button).toBeDisabled();
    });

    await ue.click(screen.getAllByRole("button", { name: "User menu" })[0]);

    expect(screen.getByRole("menuitem", { name: "Settings" })).toHaveAttribute(
      "aria-disabled",
      "true",
    );
    expect(screen.getByRole("menuitem", { name: "Logout" })).not.toHaveAttribute(
      "aria-disabled",
      "true",
    );
  });

  it("disables user-dependent actions when refetch fails with cached user info", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const navigate = vi.fn();
    vi.mocked(useNavigate).mockReturnValue(navigate);
    vi.mocked(useGetUserMeQuery).mockReturnValue({
      data: mockUserMe,
      error: { status: 500 },
      isLoading: false,
    });

    renderTopbar();

    screen.getAllByRole("button", { name: "Team menu" }).forEach((button) => {
      expect(button).toBeDisabled();
    });

    await ue.click(screen.getAllByRole("button", { name: "Team menu" })[0]);
    expect(screen.queryByRole("menuitem", { name: "Platform Team" })).not.toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();

    await ue.click(screen.getAllByRole("button", { name: "User menu" })[0]);
    expect(screen.getByRole("menuitem", { name: "Settings" })).toHaveAttribute(
      "aria-disabled",
      "true",
    );
  });

  it("navigates from the page menu while preserving shared query params", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const navigate = vi.fn();
    vi.mocked(useNavigate).mockReturnValue(navigate);
    renderTopbar({ search: "?pteamId=pteam-security&serviceId=svc-1&mytasks=on" });

    await ue.click(screen.getAllByRole("button", { name: "Page menu" })[0]);
    await ue.click(screen.getByRole("menuitem", { name: "Team Management" }));

    expect(navigate).toHaveBeenCalledWith(
      "/pteam?pteamId=pteam-security&serviceId=svc-1&mytasks=on",
    );
  });

  it("switches teams while preserving the mytasks query param", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const navigate = vi.fn();
    vi.mocked(useNavigate).mockReturnValue(navigate);
    renderTopbar({ search: "?pteamId=pteam-security&serviceId=svc-1&mytasks=on" });

    await ue.click(screen.getAllByRole("button", { name: "Team menu" })[0]);
    await ue.click(screen.getByRole("menuitem", { name: "Platform Team" }));

    expect(navigate).toHaveBeenCalledWith("/?mytasks=on&pteamId=pteam-platform");
  });

  it("opens team creation from the team menu", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    renderTopbar();

    await ue.click(screen.getAllByRole("button", { name: "Team menu" })[0]);
    await ue.click(screen.getByRole("menuitem", { name: "Create Team" }));

    expect(screen.getByText("Create Team Modal")).toBeInTheDocument();
  });

  it("does not show team selection in the user menu", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    renderTopbar();

    await ue.click(screen.getAllByRole("button", { name: "User menu" })[0]);

    expect(screen.getByRole("menuitem", { name: "Settings" })).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: "Platform Team" })).not.toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: "Create Team" })).not.toBeInTheDocument();
  });

  it("opens account settings from the user menu", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    renderTopbar();

    await ue.click(screen.getAllByRole("button", { name: "User menu" })[0]);
    await ue.click(screen.getByRole("menuitem", { name: "Settings" }));

    expect(screen.getByText("Account Settings Modal")).toBeInTheDocument();
  });

  it("resets client state and signs out from the user menu", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const dispatch = vi.fn();
    const signOut = vi.fn();
    vi.mocked(useDispatch).mockReturnValue(dispatch);
    vi.mocked(useAuth).mockReturnValue({ signOut });
    renderTopbar();

    await ue.click(screen.getAllByRole("button", { name: "User menu" })[0]);
    await ue.click(screen.getByRole("menuitem", { name: "Logout" }));

    expect(dispatch).toHaveBeenCalledWith(tcApi.util.resetApiState());
    expect(dispatch).toHaveBeenCalledWith(setAuthUserIsReady(false));
    expect(dispatch).toHaveBeenCalledWith(setRedirectedFrom({}));
    expect(signOut).toHaveBeenCalledTimes(1);
  });
});
