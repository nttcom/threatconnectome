import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SAMLAuthProvider } from "firebase/auth";
import i18n from "i18next";
import { I18nextProvider, initReactI18next } from "react-i18next";
import { Provider } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import loginEn from "../../../../public/locales/en/login.json";
import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import { useTryLoginMutation, useCreateUserMutation } from "../../../services/tcApi";
import store from "../../../store";
import { Login } from "../LoginPage";

// Initialize i18n before test execution
// eslint-disable-next-line import/no-named-as-default-member
i18n.use(initReactI18next).init({
  lng: "en",
  fallbackLng: "en",
  ns: ["login"],
  defaultNS: "login",
  resources: {
    en: {
      login: loginEn,
    },
  },
  interpolation: {
    escapeValue: false,
  },
});

const renderLogin = () => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <I18nextProvider i18n={i18n}>
          <Login />
        </I18nextProvider>
      </AuthProvider>
    </Provider>,
  );
};

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

// FIXME
/*
vi.mock("firebase/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    SAMLAuthProvider: vi.fn(),
  };
});
*/

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTryLoginMutation: vi.fn(),
    useCreateUserMutation: vi.fn(),
  };
});

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  };
});

const genApiMock = (isSuccess = true, returnValue = undefined) => {
  const mockUnwrap = isSuccess
    ? vi.fn().mockResolvedValue(returnValue)
    : vi.fn().mockRejectedValue(returnValue);
  return vi.fn().mockReturnValue({ unwrap: mockUnwrap });
};

const useAuthReturnValueBase = {
  sendEmailVerification: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
  signInWithSamlPopup: vi.fn(),
  signOut: vi.fn(),
};

describe("TestLoginPage", () => {
  afterEach(() => {
    vi.clearAllMocks();
    import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "";
  });

  describe("Email authentication", () => {
    it("Login calls signInWithEmailAndPassword with inputted values", async () => {
      const mockSignInWithEmailAndPassword = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";
      const recaptchaId = "recaptcha-container-visible-login";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(mockSignInWithEmailAndPassword).toBeCalledTimes(1);
      expect(mockSignInWithEmailAndPassword).toBeCalledWith({
        email: emailValue,
        password: passwordValue,
        recaptchaId: recaptchaId,
      });
    });

    it("Not navigate when failed signin)", async () => {
      const errorCode = "test error";
      const errorMessage = "Something went wrong.";
      const mockSignInWithEmailAndPassword = vi.fn().mockRejectedValue({
        code: errorCode,
        message: errorMessage,
      });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(0);
      expect(mockedNavigator).toBeCalledTimes(0);
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    it("Login shows error message when login failed", async () => {
      const errorCode = "test error";
      const errorMessage = "Something went wrong.";
      const mockSignInWithEmailAndPassword = vi.fn().mockRejectedValue({
        code: errorCode,
        message: errorMessage,
      });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      expect(screen.queryByText(errorMessage)).not.toBeInTheDocument();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it("Navigate when authentication successful without location.state", async () => {
      const mockSignInWithEmailAndPassword = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith({ pathname: "/", search: "" });
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    // FIXME
    it.skip("Navigate back to the page where redirected from, on auth succeeded", async () => {
      const mockSignInWithEmailAndPassword = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const fromValue = "/pteam";
      const searchValue = "?pteamId=test_id";
      //useSelector.mockReturnValue({ redirectedFrom: { from: fromValue, search: searchValue }});

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const ue = userEvent.setup();
      renderLogin();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith({
        pathname: fromValue,
        search: searchValue,
      });
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    it("Create user when No user in Tc", async () => {
      const mockSignInWithEmailAndPassword = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock(false, { data: { detail: "No such user" } });
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockCreateUser).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith("/account", {
        state: { from: "/", search: "" },
      });
    });
  });

  describe("SAML authentication", () => {
    // FIXME
    it.skip("Login calls signInWithSamlPopup", async () => {
      const mockSignInWithSamlPopup = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithSamlPopup: mockSignInWithSamlPopup,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      vi.spyOn(SAMLAuthProvider, "constructor").mockImplementation(() => {});

      import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "Test SAML ID";
      const ue = userEvent.setup();
      renderLogin();

      const loginButton = screen.getByRole("button", { name: "Log In with SAML" });
      await ue.click(loginButton);

      expect(mockSignInWithSamlPopup).toBeCalledTimes(1);
    });

    // FIXME
    it.skip("Login shows error message when login failed", async () => {
      const mockSignInWithSamlPopup = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithSamlPopup: mockSignInWithSamlPopup,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      vi.spyOn(SAMLAuthProvider, "constructor").mockImplementation(() => {});

      import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "Test SAML ID";

      const expectedMessageRegexp = new RegExp("Something went wrong.");
      expect(screen.queryByText(expectedMessageRegexp)).not.toBeInTheDocument();

      const ue = userEvent.setup();
      renderLogin();

      const loginButton = screen.getByRole("button", { name: "Log In with SAML" });
      await ue.click(loginButton);

      expect(screen.getByText(expectedMessageRegexp)).toBeInTheDocument();
    });

    // FIXME
    it.skip("Navigate when authentication successful without location.state", async () => {
      const mockSignInWithSamlPopup = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithSamlPopup: mockSignInWithSamlPopup,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      vi.spyOn(SAMLAuthProvider, "constructor").mockImplementation(() => {});

      import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "Test SAML ID";
      const ue = userEvent.setup();
      renderLogin();

      const loginButton = screen.getByRole("button", { name: "Log In with SAML" });
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith({ pathname: "/", search: "" });
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    // FIXME
    it.skip("Navigate back to the page where redirected from, on auth succeeded", async () => {
      const mockSignInWithSamlPopup = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithSamlPopup: mockSignInWithSamlPopup,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: { from: "/pteam", search: "?pteamId=test_id" } };
      useLocation.mockReturnValue(testLocation);

      vi.spyOn(SAMLAuthProvider, "constructor").mockImplementation(() => {});

      import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "Test SAML ID";
      const ue = userEvent.setup();
      renderLogin();

      const loginButton = screen.getByRole("button", { name: "Log In with SAML" });
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith({
        pathname: testLocation.state.from,
        search: testLocation.state.search,
      });
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    // FIXME
    it.skip("Create user when No user in Tc", async () => {
      const mockSignInWithSamlPopup = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithSamlPopup: mockSignInWithSamlPopup,
      });

      const mockTryLogin = genApiMock(false, { data: { detail: "No such user" } });
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      vi.spyOn(SAMLAuthProvider, "constructor").mockImplementation(() => {});

      import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "Test SAML ID";
      const ue = userEvent.setup();
      renderLogin();

      const loginButton = screen.getByRole("button", { name: "Log In with SAML" });
      await ue.click(loginButton);

      expect(mockTryLogin).toBeCalledTimes(1);
      expect(mockCreateUser).toBeCalledTimes(1);
      expect(mockedNavigator).toBeCalledTimes(1);
      expect(mockedNavigator).toHaveBeenCalledWith("/account", {
        state: { from: "/", search: "" },
      });
    });
  });

  describe("UI elements", () => {
    it("Change password mask", async () => {
      useAuth.mockReturnValue(useAuthReturnValueBase);

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const passwordField = screen.getByLabelText(/^Password/);
      const passwordValue = "secret keyword";
      await ue.type(passwordField, passwordValue);

      const passwordMaskOnButton1 = screen.getByTestId("VisibilityIcon");

      const passwordMaskOffButton1 = screen.queryByTestId("VisibilityOffIcon");
      expect(passwordMaskOffButton1).toBeNull();

      await ue.click(passwordMaskOnButton1);

      const passwordMaskOnButton2 = screen.queryByTestId("VisibilityIcon");
      expect(passwordMaskOnButton2).toBeNull();

      const passwordMaskOffButton2 = screen.getByTestId("VisibilityOffIcon");

      await ue.click(passwordMaskOffButton2);

      const passwordMaskOnButton3 = screen.queryByTestId("VisibilityIcon");
      expect(passwordMaskOnButton3).toBeInTheDocument();

      const passwordMaskOffButton3 = screen.queryByTestId("VisibilityOffIcon");
      expect(passwordMaskOffButton3).toBeNull();
    });

    it("Email and password are required", async () => {
      const mockSignInWithEmailAndPassword = vi.fn().mockResolvedValue({ originalData: undefined });
      useAuth.mockReturnValue({
        ...useAuthReturnValueBase,
        signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
      });

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      const ue = userEvent.setup();
      renderLogin();

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      expect(emailField).toBeRequired();

      const passwordField = screen.getByLabelText(/^Password/);
      expect(passwordField).toBeRequired();

      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      expect(loginButton).toBeEnabled();
      await ue.click(loginButton);
      expect(mockSignInWithEmailAndPassword).toBeCalledTimes(0);
    });

    it("Not visible SAML button without env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID", async () => {
      useAuth.mockReturnValue(useAuthReturnValueBase);

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: null };
      useLocation.mockReturnValue(testLocation);

      renderLogin();

      const samlLoginButton = screen.queryByRole("button", { name: "Log In with SAML" });
      expect(samlLoginButton).toBeNull();
    });
  });
});
