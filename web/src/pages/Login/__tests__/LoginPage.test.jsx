import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SAMLAuthProvider } from "firebase/auth";
import React from "react";
import { Provider } from "react-redux";
import { BrowserRouter, useLocation, useNavigate } from "react-router-dom";

import {
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
} from "../../../services/firebaseApi";
import { useTryLoginMutation, useCreateUserMutation } from "../../../services/tcApi";
import store from "../../../store";
import { Login } from "../LoginPage";

const renderLogin = () => {
  render(
    <Provider store={store}>
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    </Provider>,
  );
};

vi.mock("../../../services/firebaseApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSignInWithEmailAndPasswordMutation: vi.fn(),
    useSignInWithSamlPopupMutation: vi.fn(),
  };
});

vi.mock("firebase/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    SAMLAuthProvider: vi.fn(),
  };
});

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
    BrowserRouter: vi.fn().mockImplementation((props) => props.children),
  };
});

const genApiMock = (isSuccess = true, returnValue = undefined) => {
  const mockUnwrap = isSuccess
    ? vi.fn().mockResolvedValue(returnValue)
    : vi.fn().mockRejectedValue(returnValue);
  return vi.fn().mockReturnValue({ unwrap: mockUnwrap });
};

describe("TestLoginPage", () => {
  afterEach(() => {
    vi.clearAllMocks();
    import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID = "";
  });

  describe("Email authentication", () => {
    it("Login calls signInWithEmailAndPassword with inputed values", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

      expect(mockSignInWithEmailAndPassword).toBeCalledTimes(1);
      expect(mockSignInWithEmailAndPassword).toBeCalledWith({
        email: emailValue,
        password: passwordValue,
      });
    });

    it("Not navigate when userCredential is undefined)", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it.sequential.each([
      ["auth/invalid-email", /Invalid email format/],
      ["auth/too-many-requests", /Too many requests/],
      ["auth/user-disabled", /Disabled user/],
      ["auth/user-not-found", /User not found/],
      ["auth/wrong-password", /Wrong password/],
      ["unexpected-error", /Something went wrong/],
    ])("Login shows error message when login failed: %s", async (errorCode, expected) => {
      const mockSignInWithEmailAndPassword = genApiMock(false, { code: errorCode });
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

      const expectedMessageRegexp = new RegExp(expected);
      expect(screen.queryByText(expectedMessageRegexp)).not.toBeInTheDocument();

      const emailValue = "user1@localhost.localdomain";
      const passwordValue = "secret keyword";

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const passwordField = screen.getByLabelText(/^Password/);
      const loginButton = screen.getByRole("button", { name: "Log In with Email" });
      await ue.type(emailField, emailValue);
      await ue.type(passwordField, passwordValue);
      await ue.click(loginButton);

      expect(screen.getByText(expectedMessageRegexp)).toBeInTheDocument();
    });

    it("Navigate when authentication successful without location.state", async () => {
      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithEmailAndPassword = genApiMock(true, testCredential);
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it("Navigate back to the page where redirected from, on auth succeeded", async () => {
      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithEmailAndPassword = genApiMock(true, testCredential);
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

      const mockTryLogin = genApiMock();
      useTryLoginMutation.mockReturnValue([mockTryLogin]);

      const mockCreateUser = genApiMock();
      useCreateUserMutation.mockReturnValue([mockCreateUser]);

      const mockedNavigator = vi.fn();
      useNavigate.mockReturnValue(mockedNavigator);

      const testLocation = { state: { from: "/pteam", search: "?pteamId=test_id" } };
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
      expect(mockedNavigator).toHaveBeenCalledWith({
        pathname: testLocation.state.from,
        search: testLocation.state.search,
      });
      expect(mockCreateUser).toBeCalledTimes(0);
    });

    it("Create user when No user in Tc", async () => {
      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithEmailAndPassword = genApiMock(true, testCredential);
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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
    it("Login calls signInWithSamlPopup", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithSamlPopup = genApiMock(true, testCredential);
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it("Login shows error message when login failed", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock(false);
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it("Navigate when authentication successful without location.state", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithSamlPopup = genApiMock(true, testCredential);
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it("Navigate back to the page where redirected from, on auth succeeded", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithSamlPopup = genApiMock(true, testCredential);
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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

    it("Create user when No user in Tc", async () => {
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const testCredential = { user: { accessToken: "test_token" } };
      const mockSignInWithSamlPopup = genApiMock(true, testCredential);
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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
      const mockSignInWithEmailAndPassword = genApiMock();
      useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

      const mockSignInWithSamlPopup = genApiMock();
      useSignInWithSamlPopupMutation.mockReturnValue([mockSignInWithSamlPopup]);

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
