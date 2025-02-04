import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { useApplyActionCodeMutation } from "../../../services/firebaseApi";
import store from "../../../store";
import VerifyEmail from "../VerifyEmail";

vi.mock("../../../services/firebaseApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useApplyActionCodeMutation: vi.fn(),
  };
});

const renderVerifyEmail = () => {
  render(
    <Provider store={store}>
      <VerifyEmail />
    </Provider>,
  );
};

describe("TestVerifyEmail", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const ApplyActionCodeMock = vi.fn();
      const mockUnwrap = vi.fn().mockResolvedValue();
      ApplyActionCodeMock.mockReturnValue({ unwrap: mockUnwrap });
      vi.mocked(useApplyActionCodeMutation).mockReturnValue([ApplyActionCodeMock]);
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      renderVerifyEmail();
      expect(screen.getByRole("heading", { name: /Email Verification/i })).toBeInTheDocument();
    });

    it("renders the verify email button", () => {
      renderVerifyEmail();
      expect(screen.getByRole("button", { name: /Verify Email/i })).toBeInTheDocument();
    });
  });

  describe("Verify email button behabior", () => {
    it("triggers verification when the verify email button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const ApplyActionCodeMock = vi.fn();
      const mockUnwrap = vi.fn().mockResolvedValue();
      ApplyActionCodeMock.mockReturnValue({ unwrap: mockUnwrap });
      vi.mocked(useApplyActionCodeMutation).mockReturnValue([ApplyActionCodeMock]);

      renderVerifyEmail();
      await ue.click(screen.getByRole("button", { name: /Verify Email/i }));
      expect(screen.getByRole("button", { name: /Verify Email/i })).toBeDisabled();
      expect(screen.getByText(/email verification success/)).toBeInTheDocument();
    });

    it("handles error", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const ApplyActionCodeMock = vi.fn();
      const mockUnwrap = vi.fn().mockRejectedValue();
      ApplyActionCodeMock.mockReturnValue({ unwrap: mockUnwrap });
      vi.mocked(useApplyActionCodeMutation).mockReturnValue([ApplyActionCodeMock]);

      renderVerifyEmail();
      await ue.click(screen.getByRole("button", { name: /Verify Email/i }));
      expect(screen.getByRole("button", { name: /Verify Email/i })).toBeDisabled();
      expect(screen.getByText(/something went wrong/)).toBeInTheDocument();
    });
  });
});
