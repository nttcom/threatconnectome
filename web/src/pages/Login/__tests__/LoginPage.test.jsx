import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import { useSignInWithEmailAndPasswordMutation } from "../../../services/firebaseApi";
import { useTryLoginMutation, useCreateUserMutation } from "../../../services/tcApi";
import store from "../../../store";
import { Login } from "../LoginPage";

const renderLogin = () => {
  render(
    <Provider store={store}>
      <BrowserRouter
        future={{
          /* to prevent React Router Future Flag Warning.
           * see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath for details.
           */
          // v7_fetcherPersist: true,
          // v7_normalizeFormMethod: true,
          // v7_partialHydration: true,
          v7_relativeSplatPath: true,
          // v7_skipActionErrorRevalidation: true,
          v7_startTransition: true,
        }}
      >
        <Login />
      </BrowserRouter>
    </Provider>,
  );
};

jest.mock("../../../services/firebaseApi", () => ({
  ...jest.requireActual("../../../services/firebaseApi"),
  useSignInWithEmailAndPasswordMutation: jest.fn(),
}));

jest.mock("../../../services/tcApi", () => ({
  ...jest.requireActual("../../../services/tcApi"),
  useTryLoginMutation: jest.fn(),
  useCreateUserMutation: jest.fn(),
}));

const mockedNavigator = jest.fn();
const testLocation = { state: null };
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigator,
  useLocation: () => testLocation,
}));

const genApiMock = (isSuccess = true, returnValue = undefined) => {
  const mockUnwrap = isSuccess
    ? jest.fn().mockResolvedValue(returnValue)
    : jest.fn().mockRejectedValue(returnValue);
  return jest.fn().mockReturnValue({ unwrap: mockUnwrap });
};

describe("TestLoginPage", () => {
  afterEach(() => {
    jest.clearAllMocks();
    testLocation.state = null;
  });

  it("Login calls signInWithEmailAndPassword with inputed values", async () => {
    const mockSignInWithEmailAndPassword = genApiMock();
    useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

    const mockTryLogin = genApiMock();
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

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

    const mockTryLogin = genApiMock();
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

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

  it.concurrent.each([
    ["auth/invalid-email", /Invalid email format/],
    ["auth/too-many-requests", /Too many requests/],
    ["auth/user-disabled", /Disabled user/],
    ["auth/user-not-found", /User not found/],
    ["auth/wrong-password", /Wrong password/],
    ["unexpected-error", /Something went wrong/],
  ])("Login shows error message when login failed: %s", async (errorCode, expected) => {
    const mockSignInWithEmailAndPassword = genApiMock(false, { code: errorCode });
    useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);

    const mockTryLogin = genApiMock();
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

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

    const mockTryLogin = genApiMock();
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

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

    const mockTryLogin = genApiMock();
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

    testLocation.state = { from: "/pteam", search: "?pteamId=test_id" };

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

    const mockTryLogin = genApiMock(false, { data: { detail: "No such user" } });
    useTryLoginMutation.mockReturnValue([mockTryLogin]);

    const mockCreateUser = genApiMock();
    useCreateUserMutation.mockReturnValue([mockCreateUser]);

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
    expect(mockedNavigator).toHaveBeenCalledWith("/account", { state: { from: "/", search: "" } });
  });
});
