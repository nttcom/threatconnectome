import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import store from "../../../store";
import { ResetPassword } from "../ResetPasswordPage";

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

const renderResetPassword = () => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <BrowserRouter
          future={{
            /* to prevent React Router Future Flag Warning.
             * see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath for details.
             */
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <ResetPassword />
        </BrowserRouter>
      </AuthProvider>
    </Provider>,
  );
};

const genApiMock = (isSuccess = true, returnValue = undefined) => {
  const mockUnwrap = isSuccess
    ? vi.fn().mockResolvedValue(returnValue)
    : vi.fn().mockRejectedValue(returnValue);
  return vi.fn().mockReturnValue({ unwrap: mockUnwrap });
};

describe("ResetPassword Component", () => {
  describe("Rendering", () => {
    it("should render ResetPassword form", () => {
      const mockSendPasswordResetEmail = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({ sendPasswordResetEmail: mockSendPasswordResetEmail });

      renderResetPassword();

      expect(screen.getByRole("textbox", { name: "Email Address" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Reset Password" })).toBeInTheDocument();
      expect(screen.getByText("Back to log in")).toBeInTheDocument();
    });
  });

  it("should call auth API with correct parameters", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const mockSendPasswordResetEmail = vi.fn().mockResolvedValue();
    useAuth.mockReturnValue({ sendPasswordResetEmail: mockSendPasswordResetEmail });

    renderResetPassword();

    const emailField = screen.getByRole("textbox", { name: "Email Address" });
    const submitButton = screen.getByRole("button", { name: "Reset Password" });

    const emailValue = "test@example.com";
    await ue.type(emailField, emailValue);
    await ue.click(submitButton);

    expect(mockSendPasswordResetEmail).toHaveBeenCalledWith({
      email: emailValue,
      actionCodeSettings: expect.any(Object),
      redirectTo: expect.any(String),
    });

    expect(
      screen.getByText(new RegExp("An email with a password reset URL was sent to this address.")),
    ).toBeInTheDocument();
  });

  describe("Error Handling", () => {
    it("should show error message when email is invalid", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockSendPasswordResetEmail = vi.fn().mockRejectedValue({
        code: "auth/invalid-email",
        message: "Invalid email format.",
      });
      useAuth.mockReturnValue({ sendPasswordResetEmail: mockSendPasswordResetEmail });

      renderResetPassword();

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const resetButton = screen.getByRole("button", { name: "Reset Password" });

      await ue.type(emailField, "invalid-email");
      await ue.click(resetButton);

      expect(screen.getByText("Invalid email format.")).toBeInTheDocument();
    });

    it("should show error message when user does not exist", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockSendPasswordResetEmail = vi.fn().mockRejectedValue({
        code: "auth/user-not-found",
        message: "User not found.",
      });
      useAuth.mockReturnValue({ sendPasswordResetEmail: mockSendPasswordResetEmail });

      renderResetPassword();

      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      const resetButton = screen.getByRole("button", { name: "Reset Password" });

      await ue.type(emailField, "nonexistentuser@example.com");
      await ue.click(resetButton);

      expect(screen.getByText("User not found.")).toBeInTheDocument();
    });
  });

  describe("Form Validation", () => {
    it("should not call the callback when the Reset Password button is clicked and email is empty", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockSendPasswordResetEmail = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({ sendPasswordResetEmail: mockSendPasswordResetEmail });

      renderResetPassword();

      const resetButton = screen.getByRole("button", { name: "Reset Password" });

      await ue.click(resetButton);

      expect(mockSendPasswordResetEmail).not.toHaveBeenCalled();
    });
  });
});
