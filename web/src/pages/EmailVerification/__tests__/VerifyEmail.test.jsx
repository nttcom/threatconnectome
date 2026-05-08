import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import { Provider } from "react-redux";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import store from "../../../store";
import VerifyEmail from "../VerifyEmail";

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

const renderVerifyEmail = () => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <VerifyEmail />
      </AuthProvider>
    </Provider>,
  );
};

describe("TestVerifyEmail", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const mockApplyActionCode = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({ applyActionCode: mockApplyActionCode });
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      renderVerifyEmail();
      expect(screen.getByRole("heading", { name: "Email Verification" })).toBeInTheDocument();
    });

    it("renders the verify email button", () => {
      renderVerifyEmail();
      expect(screen.getByRole("button", { name: "Verify Email" })).toBeInTheDocument();
    });
  });

  describe("Verify email button behavior", () => {
    it("triggers verification when the verify email button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockApplyActionCode = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({ applyActionCode: mockApplyActionCode });

      renderVerifyEmail();
      await ue.click(screen.getByRole("button", { name: "Verify Email" }));
      expect(screen.getByRole("button", { name: "Verify Email" })).toBeDisabled();
      expect(screen.getByText(/email verification success/)).toBeInTheDocument();
    });

    it("handles error", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const errorCode = "error code";
      const errorMessage = "Something went wrong.";
      const mockApplyActionCode = vi
        .fn()
        .mockRejectedValue({ code: errorCode, message: errorMessage });
      useAuth.mockReturnValue({ applyActionCode: mockApplyActionCode });
      const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

      renderVerifyEmail();
      await ue.click(screen.getByRole("button", { name: "Verify Email" }));
      expect(mockConsoleError).toHaveBeenCalledWith({
        code: errorCode,
        message: errorMessage,
      });
      expect(screen.getByRole("button", { name: "Verify Email" })).toBeDisabled();
      expect(screen.getByText(new RegExp(errorMessage))).toBeInTheDocument();
    });
  });
});
