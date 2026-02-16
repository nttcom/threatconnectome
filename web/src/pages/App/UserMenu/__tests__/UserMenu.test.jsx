import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import i18n from "i18next";
import { I18nextProvider, initReactI18next } from "react-i18next";
import { Provider, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import appEn from "../../../../../public/locales/en/app.json";
import { useAuth, useSkipUntilAuthUserIsReady } from "../../../../hooks/auth";
import { AuthProvider } from "../../../../providers/auth/AuthContext";
import { tcApi, useGetUserMeQuery } from "../../../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../../../slices/auth";
import store from "../../../../store";
import { UserMenu } from "../UserMenu";

// Initialize i18n before test execution
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

vi.mock("../../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

vi.mock("../../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetUserMeQuery: vi.fn(),
  };
});

const renderUserMenu = () => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <I18nextProvider i18n={i18n}>
          <UserMenu />
        </I18nextProvider>
      </AuthProvider>
    </Provider>,
  );
};

describe("TestUserMenu", () => {
  const mockGetUserMeQuery = {
    data: {
      user_id: "00000000-0000-0000-0000-0000000000",
      uid: "0000000000000000000000000000",
      email: "test@example",
      disabled: false,
      years: 0,
      pteam_roles: [
        {
          is_admin: true,
          pteam: {
            pteam_id: "11111111-1111-1111-1111-1111111111",
            pteam_name: "test_pteam",
            contact_info: "test_contact_info",
          },
        },
      ],
    },
    error: null,
    isLoading: false,
  };

  describe("Rendering", () => {
    it("UserMenu renders", () => {
      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({
        signOut: mockSignOut,
        isAuthenticatedWithSaml: vi.fn().mockReturnValue(false),
      });

      const mockSkipUntilAuthUserIsReady = false;
      useSkipUntilAuthUserIsReady.mockReturnValue(mockSkipUntilAuthUserIsReady);

      vi.mocked(useGetUserMeQuery).mockReturnValue(mockGetUserMeQuery);

      renderUserMenu();

      expect(screen.getByRole("button", { name: "user menu" })).toBeInTheDocument();
    });
    it("should render Logout and Settings buttons when the user menu is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({
        signOut: mockSignOut,
        isAuthenticatedWithSaml: vi.fn().mockReturnValue(false),
      });

      const mockSkipUntilAuthUserIsReady = false;
      useSkipUntilAuthUserIsReady.mockReturnValue(mockSkipUntilAuthUserIsReady);

      vi.mocked(useGetUserMeQuery).mockReturnValue(mockGetUserMeQuery);

      renderUserMenu();

      await ue.click(screen.getByRole("button", { name: "user menu" }));

      expect(screen.getByRole("menuitem", { name: "Settings" })).toBeInTheDocument();
      expect(screen.getByRole("menuitem", { name: "Logout" })).toBeInTheDocument();
    });
  });
  describe("Logout Behavior", () => {
    it("resets API states and navigates to login when the Logout button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockDispatch = vi.fn();
      vi.mocked(useDispatch).mockReturnValue(mockDispatch);

      const mockNavigate = vi.fn();
      vi.mocked(useNavigate).mockReturnValue(mockNavigate);

      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({
        signOut: mockSignOut,
        isAuthenticatedWithSaml: vi.fn().mockReturnValue(false),
      });

      const mockSkipUntilAuthUserIsReady = false;
      useSkipUntilAuthUserIsReady.mockReturnValue(mockSkipUntilAuthUserIsReady);

      vi.mocked(useGetUserMeQuery).mockReturnValue(mockGetUserMeQuery);

      renderUserMenu();

      await ue.click(screen.getByRole("button", { name: "user menu" }));
      await ue.click(screen.getByRole("menuitem", { name: "Logout" }));

      expect(mockDispatch).toHaveBeenCalledWith(tcApi.util.resetApiState());
      expect(mockDispatch).toHaveBeenCalledWith(setAuthUserIsReady(false));
      expect(mockDispatch).toHaveBeenCalledWith(setRedirectedFrom({}));
      expect(mockSignOut).toBeCalledTimes(1);
    });
  });
});
