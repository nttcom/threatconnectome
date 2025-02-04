import { render, screen } from "@testing-library/react";
import React from "react";
import { Provider, useDispatch } from "react-redux";
import { useLocation } from "react-router-dom";

import store from "../../../store";
import { EmailVerification } from "../EmailVerificationPage";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  };
});

vi.mock("react-redux", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useDispatch: vi.fn(),
  };
});

const renderEmailVerification = () => {
  render(
    <Provider store={store}>
      <EmailVerification />
    </Provider>,
  );
};

describe("TestEmailVerificationPage", () => {
  it("renders ResetPasswordForm when mode=resetPassword", async () => {
    const testLocation = { search: "?mode=resetPassword&oobCode=00000" };
    useLocation.mockReturnValue(testLocation);

    renderEmailVerification();
    expect(screen.getByText("Reset Password")).toBeInTheDocument();
  });

  it("renders VerifyEmail when mode=resetPassword", async () => {
    const testLocation = { search: "?mode=verifyEmail&oobCode=00000" };
    useLocation.mockReturnValue(testLocation);

    renderEmailVerification();
    expect(screen.getByText("Email Verification")).toBeInTheDocument();
  });

  it("calls console.error when mode is invalid", async () => {
    const testLocation = { search: "?mode=invalidmode&oobCode=00000" };
    useLocation.mockReturnValue(testLocation);

    const consoleErrorMock = vi.spyOn(console, "error").mockImplementation(() => {});

    renderEmailVerification();
    expect(consoleErrorMock).toHaveBeenCalledWith("Invalid mode");
  });
});
