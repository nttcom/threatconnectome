import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import { Provider } from "react-redux";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import store from "../../../store";
import ResetPasswordForm from "../ResetPasswordForm";

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

const renderVerifyEmail = (oobCode) => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <ResetPasswordForm oobCode={oobCode} />
      </AuthProvider>
    </Provider>,
  );
};

describe("TestResetPasswordForm", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const mockVerifyPasswordResetCode = vi.fn();
      const mockConfirmPasswordReset = vi.fn();
      useAuth.mockReturnValue({
        verifyPasswordResetCode: mockVerifyPasswordResetCode,
        confirmPasswordReset: mockConfirmPasswordReset,
      });
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      const oobCodeExample = "00000";
      renderVerifyEmail(oobCodeExample);
      expect(screen.getByRole("heading", { name: "Reset Password" })).toBeInTheDocument();
    });

    it("renders the password input field", () => {
      const oobCodeExample = "00000";
      renderVerifyEmail(oobCodeExample);
      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      expect(passwordField).toBeRequired();
    });

    it("renders the submit button", () => {
      const oobCodeExample = "00000";
      renderVerifyEmail(oobCodeExample);
      expect(screen.getByRole("button", { name: "Submit" })).toBeInTheDocument();
    });
  });

  describe("Submit button behavior", () => {
    it("triggers password reset when the submit button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const oobCodeExample = "00000";
      const validPassword = "Password1234@";

      const mockVerifyPasswordResetCode = vi.fn().mockResolvedValue();
      const mockConfirmPasswordReset = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({
        verifyPasswordResetCode: mockVerifyPasswordResetCode,
        confirmPasswordReset: mockConfirmPasswordReset,
      });

      renderVerifyEmail(oobCodeExample);

      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, validPassword);

      await ue.click(screen.getByRole("button", { name: "Submit" }));

      expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
      expect(mockVerifyPasswordResetCode).toHaveBeenCalledWith({
        actionCode: oobCodeExample,
      });

      expect(mockConfirmPasswordReset).toHaveBeenCalledWith({
        actionCode: oobCodeExample,
        newPassword: validPassword,
      });
      expect(screen.getByText(/update password success/)).toBeInTheDocument();
    });

    it("handles error", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const oobCodeExample = "00000";
      const validPassword = "Password1234@";
      const errorCode = "error";
      const errorMessage = "Something went wrong.";

      const mockVerifyPasswordResetCode = vi.fn().mockRejectedValue({
        code: errorCode,
        message: errorMessage,
      });
      const mockConfirmPasswordReset = vi.fn();
      useAuth.mockReturnValue({
        verifyPasswordResetCode: mockVerifyPasswordResetCode,
        confirmPasswordReset: mockConfirmPasswordReset,
      });
      const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

      renderVerifyEmail(oobCodeExample);

      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, validPassword);

      await ue.click(screen.getByRole("button", { name: "Submit" }));

      expect(mockConsoleError).toHaveBeenCalledWith({
        code: errorCode,
        message: errorMessage,
      });

      expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
      expect(mockVerifyPasswordResetCode).toHaveBeenCalledWith({
        actionCode: oobCodeExample,
      });

      expect(screen.getByText(new RegExp(errorMessage))).toBeInTheDocument();
    });
  });

  it("change password mask when click visibility icon button", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const oobCodeExample = "00000";

    renderVerifyEmail(oobCodeExample);
    const passwordFields = screen.getAllByLabelText(/^New Password/);
    const passwordField = passwordFields.find((el) => el.tagName === "INPUT");

    expect(passwordField).toHaveAttribute("type", "password");

    await ue.click(screen.getByLabelText("toggle password visibility"));

    expect(passwordField).toHaveAttribute("type", "text");
  });
});
