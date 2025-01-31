import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";

import { useSendPasswordResetEmailMutation } from "../../../services/firebaseApi";
import store from "../../../store";
import { ResetPassword } from "../ResetPasswordPage";

vi.mock("../../../services/firebaseApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSendPasswordResetEmailMutation: vi.fn(),
  };
});

const renderResetPassword = () => {
  render(
    <Provider store={store}>
      <BrowserRouter>
        <ResetPassword />
      </BrowserRouter>
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
      const sendPasswordResetEmailMock = vi.fn();
      const mockUnwrap = vi.fn().mockResolvedValue();
      sendPasswordResetEmailMock.mockReturnValue({ unwrap: mockUnwrap });

      vi.mocked(useSendPasswordResetEmailMutation).mockReturnValue([sendPasswordResetEmailMock]);

      renderResetPassword();

      expect(screen.getByRole("textbox", { name: /email address/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /reset password/i })).toBeInTheDocument();
      expect(screen.getByText("Back to log in")).toBeInTheDocument();
    });
  });

  it("should call firebase API with correct parameters", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const sendPasswordResetEmailMock = vi.fn();
    const mockUnwrap = vi.fn().mockResolvedValue();
    sendPasswordResetEmailMock.mockReturnValue({ unwrap: mockUnwrap });
    vi.mocked(useSendPasswordResetEmailMutation).mockReturnValue([sendPasswordResetEmailMock]);

    renderResetPassword();

    const emailField = screen.getByRole("textbox", { name: /email address/i });
    const resetButton = screen.getByRole("button", { name: /reset password/i });

    await ue.type(emailField, "test@example.com");
    await ue.click(resetButton);

    expect(sendPasswordResetEmailMock).toHaveBeenCalledWith({
      email: "test@example.com",
      actionCodeSettings: expect.any(Object),
    });

    expect(
      screen.getByText("An email with a password reset URL was sent to this address."),
    ).toBeInTheDocument();
  });

  describe("Error Handling", () => {
    it("should show error message when email is invalid", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const sendPasswordResetEmailMock = vi.fn();
      vi.mocked(useSendPasswordResetEmailMutation).mockReturnValue([sendPasswordResetEmailMock]);

      const mockSendPasswordResetEmail = genApiMock(false, { code: "auth/invalid-email" });
      useSendPasswordResetEmailMutation.mockReturnValue([mockSendPasswordResetEmail]);

      renderResetPassword();

      const emailField = screen.getByRole("textbox", { name: /email address/i });
      const resetButton = screen.getByRole("button", { name: /reset password/i });

      await ue.type(emailField, "invalid-email");
      await ue.click(resetButton);

      expect(screen.getByText("Invalid email format.")).toBeInTheDocument();
    });

    it("should show error message when user does not exist", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const sendPasswordResetEmailMock = vi.fn();
      vi.mocked(useSendPasswordResetEmailMutation).mockReturnValue([sendPasswordResetEmailMock]);

      const mockSendPasswordResetEmail = genApiMock(false, { code: "auth/user-not-found" });
      useSendPasswordResetEmailMutation.mockReturnValue([mockSendPasswordResetEmail]);

      renderResetPassword();

      const emailField = screen.getByRole("textbox", { name: /email address/i });
      const resetButton = screen.getByRole("button", { name: /reset password/i });

      await ue.type(emailField, "nonexistentuser@example.com");
      await ue.click(resetButton);

      expect(screen.getByText("User does not exist. Check the email address.")).toBeInTheDocument();
    });
  });

  describe("Form Validation", () => {
    it("should not call the callback when the Reset Password button is clicked and email is empty", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

      const mockSendPasswordResetEmail = vi.fn();
      vi.mocked(useSendPasswordResetEmailMutation).mockReturnValue([mockSendPasswordResetEmail]);

      renderResetPassword();

      const resetButton = screen.getByRole("button", { name: /reset password/i });

      await ue.click(resetButton);

      expect(mockSendPasswordResetEmail).not.toHaveBeenCalled();
    });
  });
});
