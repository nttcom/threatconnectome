import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import {
  useVerifyPasswordResetCodeMutation,
  useConfirmPasswordResetMutation,
} from "../../../services/firebaseApi";
import store from "../../../store";
import ResetPasswordForm from "../ResetPasswordForm";

vi.mock("../../../services/firebaseApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useVerifyPasswordResetCodeMutation: vi.fn(),
    useConfirmPasswordResetMutation: vi.fn(),
  };
});

const renderVerifyEmail = (oobCode) => {
  render(
    <Provider store={store}>
      <ResetPasswordForm oobCode={oobCode} />
    </Provider>,
  );
};

describe("TestResetPasswordForm", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const VerifyPasswordResetCodeMock = vi.fn();
      VerifyPasswordResetCodeMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useVerifyPasswordResetCodeMutation.mockReturnValue([VerifyPasswordResetCodeMock]);

      const ConfirmPasswordResetMock = vi.fn();
      ConfirmPasswordResetMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useConfirmPasswordResetMutation.mockReturnValue([ConfirmPasswordResetMock]);
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      renderVerifyEmail("00000");
      expect(screen.getByRole("heading", { name: /Reset Password/i })).toBeInTheDocument();
    });

    it("renders the password input field", () => {
      renderVerifyEmail("00000");
      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      expect(passwordField).toBeRequired();
    });

    it("renders the submit button", () => {
      renderVerifyEmail("00000");
      expect(screen.getByRole("button", { name: /submit/i })).toBeInTheDocument();
    });
  });

  describe("Submit button behabior", () => {
    it("triggers password reset when the submit button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

      const VerifyPasswordResetCodeMock = vi.fn();
      VerifyPasswordResetCodeMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useVerifyPasswordResetCodeMutation.mockReturnValue([VerifyPasswordResetCodeMock]);

      const ConfirmPasswordResetMock = vi.fn();
      ConfirmPasswordResetMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useConfirmPasswordResetMutation.mockReturnValue([ConfirmPasswordResetMock]);

      renderVerifyEmail("00000");

      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, "Password1234@");

      await ue.click(screen.getByRole("button", { name: /submit/i }));

      expect(screen.getByRole("button", { name: /submit/i })).toBeDisabled();
      expect(VerifyPasswordResetCodeMock).toHaveBeenCalledWith({
        actionCode: "00000",
      });

      expect(ConfirmPasswordResetMock).toHaveBeenCalledWith({
        actionCode: "00000",
        newPassword: "Password1234@",
      });
      expect(screen.getByText(/update password success/)).toBeInTheDocument();
    });

    it("handles error", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

      const VerifyPasswordResetCodeMock = vi.fn();
      VerifyPasswordResetCodeMock.mockReturnValue({ unwrap: vi.fn().mockRejectedValue() });
      useVerifyPasswordResetCodeMutation.mockReturnValue([VerifyPasswordResetCodeMock]);

      const ConfirmPasswordResetMock = vi.fn();
      ConfirmPasswordResetMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useConfirmPasswordResetMutation.mockReturnValue([ConfirmPasswordResetMock]);

      renderVerifyEmail("00000");

      const passwordFields = screen.getAllByLabelText(/^New Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, "Password1234@");

      await ue.click(screen.getByRole("button", { name: /submit/i }));

      expect(screen.getByRole("button", { name: /submit/i })).toBeDisabled();
      expect(VerifyPasswordResetCodeMock).toHaveBeenCalledWith({
        actionCode: "00000",
      });

      expect(screen.getByText(/something went wrong/)).toBeInTheDocument();
    });
  });
  it("change password mask when click visibility icon button", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    renderVerifyEmail("00000");
    const passwordFields = screen.getAllByLabelText(/^New Password/);
    const passwordField = passwordFields.find((el) => el.tagName === "INPUT");

    expect(passwordField).toHaveAttribute("type", "password");

    await ue.click(screen.getByLabelText("toggle password visibility"));

    expect(passwordField).toHaveAttribute("type", "text");
  });
});
