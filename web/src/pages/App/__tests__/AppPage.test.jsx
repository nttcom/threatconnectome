import { render, screen } from "@testing-library/react";
import i18n from "i18next";
import { I18nextProvider, initReactI18next } from "react-i18next";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import appEn from "../../../../public/locales/en/app.json";
import { useAuth } from "../../../hooks/auth";
import { setRedirectedFrom } from "../../../slices/auth";
import { App } from "../AppPage";

let topbarShouldThrow = false;

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

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

vi.mock("../Topbar", () => ({
  Topbar: () => {
    if (topbarShouldThrow) {
      throw new Error("Topbar failed");
    }
    return <nav aria-label="New topbar">New topbar</nav>;
  },
}));

vi.mock("../OutletWithCheckedParams", () => ({
  OutletWithCheckedParams: () => <main>Checked outlet</main>,
}));

function renderApp() {
  render(
    <I18nextProvider i18n={i18n}>
      <App />
    </I18nextProvider>,
  );
}

describe("AppPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    topbarShouldThrow = false;
    vi.mocked(useDispatch).mockReturnValue(vi.fn());
    vi.mocked(useNavigate).mockReturnValue(vi.fn());
    vi.mocked(useLocation).mockReturnValue({ pathname: "/", search: "?pteamId=pteam-security" });
    vi.mocked(useAuth).mockReturnValue({
      onAuthStateChanged: vi.fn(() => vi.fn()),
    });
  });

  it("renders the topbar and checked outlet without the legacy drawer shell", () => {
    renderApp();

    expect(screen.getByRole("navigation", { name: "New topbar" })).toBeInTheDocument();
    expect(screen.getByText("Checked outlet")).toBeInTheDocument();
    expect(screen.queryByLabelText("menu")).not.toBeInTheDocument();
  });

  it("stores the current location for auth redirects", () => {
    const dispatch = vi.fn();
    vi.mocked(useDispatch).mockReturnValue(dispatch);

    renderApp();

    expect(dispatch).toHaveBeenCalledWith(
      setRedirectedFrom({ from: "/", search: "?pteamId=pteam-security" }),
    );
  });

  it("contains topbar errors without replacing the checked outlet", () => {
    topbarShouldThrow = true;

    renderApp();

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByText("Checked outlet")).toBeInTheDocument();
  });
});
