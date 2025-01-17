import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import {
  useSignInWithEmailAndPasswordMutation,
  // useSignInWithSamlMutation,
} from "../../../services/firebaseApi";
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
  // useSignInWithSamlMutation: jest.fn(),
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
  });

  it("Login calls signInWithEmailAndPassword with inputed values", async () => {
    const mockSignInWithEmailAndPassword = genApiMock();
    useSignInWithEmailAndPasswordMutation.mockReturnValue([mockSignInWithEmailAndPassword]);
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
});
