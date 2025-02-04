import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider } from "react-redux";
import { useNavigate, useLocation } from "react-router-dom";
import {
  useCreateUserWithEmailAndPasswordMutation,
  useSendEmailVerificationMutation,
} from "../../../services/firebaseApi";
import store from "../../../store";
import { SignUp } from "../SignUpPage";

vi.mock("../../../services/firebaseApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useCreateUserWithEmailAndPasswordMutation: vi.fn(),
    useSendEmailVerificationMutation: vi.fn(),
  };
});

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  };
});

const renderSignUp = () => {
  render(
    <Provider store={store}>
      <SignUp />
    </Provider>,
  );
};

describe("TestSignUpPage", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const CreateUserWithEmailAndPasswordMutationMock = vi.fn();
      CreateUserWithEmailAndPasswordMutationMock.mockReturnValue({
        unwrap: vi.fn().mockResolvedValue(),
      });
      useCreateUserWithEmailAndPasswordMutation.mockReturnValue([
        CreateUserWithEmailAndPasswordMutationMock,
      ]);

      const SendEmailVerificationMock = vi.fn();
      SendEmailVerificationMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue() });
      useSendEmailVerificationMutation.mockReturnValue([SendEmailVerificationMock]);
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      renderSignUp();
      expect(screen.getByRole("heading", { name: /Threatconnectome/i })).toBeInTheDocument();
    });

    it("renders the email input field", () => {
      renderSignUp();
      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      expect(emailField).toBeRequired();
    });

    it("renders the password input field", () => {
      renderSignUp();
      const passwordFields = screen.getAllByLabelText(/^Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      expect(passwordField).toBeRequired();
    });

    it("renders the sign-up button", () => {
      renderSignUp();
      expect(screen.getByRole("button", { name: /sign up/i })).toBeInTheDocument();
    });

    it("renders the back to login link", () => {
      renderSignUp();
      expect(screen.getByRole("button", { name: /Back to log in/i })).toBeInTheDocument();
    });
  });

  describe("Sian up button behabior", () => {
    it("creates an account when given valid parameters", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

      const CreateUserWithEmailAndPasswordMutationMock = vi.fn(({ email }) => ({
        unwrap: vi.fn().mockResolvedValue({
          user: { email: email, uid: "12345" },
        }),
      }));

      useCreateUserWithEmailAndPasswordMutation.mockReturnValue([
        CreateUserWithEmailAndPasswordMutationMock,
      ]);
      const SendEmailVerificationMock = vi.fn();
      SendEmailVerificationMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue(undefined) });
      useSendEmailVerificationMutation.mockReturnValue([SendEmailVerificationMock]);

      renderSignUp();
      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      await ue.type(emailField, "test@example.com");

      const passwordFields = screen.getAllByLabelText(/^Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, "Password1234@");

      await ue.click(screen.getByRole("button", { name: /sign up/i }));

      expect(CreateUserWithEmailAndPasswordMutationMock).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "Password1234@",
      });

      expect(SendEmailVerificationMock).toHaveBeenCalledWith({
        user: { email: "test@example.com", uid: "12345" },
        actionCodeSettings: null,
      });

      expect(
        screen.getByText("An email for verification was sent to your address."),
      ).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /sign up/i })).toBeDisabled();
    });
    it.sequential.each([
      ["auth/internal-error", "Unauthorized Email Domain."],
      ["auth/email-already-in-use", "Email already in use."],
      ["auth/invalid-email", "Invalid email format."],
      ["auth/too-many-requests", "Too many requests."],
      ["auth/weak-password", "Weak password. Password should be at least 6 characters."],
      ["auth/operation-not-allowed", "Something went wrong."],
      ["other errors", "Something went wrong."],
    ])("handles error for %s", async (error_code, error_message) => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

      const CreateUserWithEmailAndPasswordMutationMock = vi.fn(() => ({
        unwrap: vi.fn().mockRejectedValue({
          code: error_code,
        }),
      }));

      useCreateUserWithEmailAndPasswordMutation.mockReturnValue([
        CreateUserWithEmailAndPasswordMutationMock,
      ]);
      const SendEmailVerificationMock = vi.fn();
      SendEmailVerificationMock.mockReturnValue({ unwrap: vi.fn().mockResolvedValue(undefined) });
      useSendEmailVerificationMutation.mockReturnValue([SendEmailVerificationMock]);

      renderSignUp();
      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      await ue.type(emailField, "test@example.com");

      const passwordFields = screen.getAllByLabelText(/^Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, "Password1234@");

      await ue.click(screen.getByRole("button", { name: /sign up/i }));

      expect(CreateUserWithEmailAndPasswordMutationMock).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "Password1234@",
      });

      expect(screen.getByText(error_message)).toBeInTheDocument();
    });
  });

  it("navigate login page when click link button", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    const navigateMock = vi.fn();
    useNavigate.mockReturnValue(navigateMock);

    const locationMock = {
      state: { from: "/test_from", search: "/test_from" },
    };
    useLocation.mockReturnValue(locationMock);

    renderSignUp();
    await ue.click(screen.getByRole("button", { name: /Back to log in/i }));

    expect(navigateMock).toHaveBeenCalledWith("/login", {
      state: {
        from: locationMock.state.from,
        search: locationMock.state.search,
      },
    });
  });

  it("change password mask when click visibility icon button", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    renderSignUp();
    const passwordFields = screen.getAllByLabelText(/^Password/);
    const passwordField = passwordFields.find((el) => el.tagName === "INPUT");

    expect(passwordField).toHaveAttribute("type", "password");

    await ue.click(screen.getByLabelText("toggle password visibility"));

    expect(passwordField).toHaveAttribute("type", "text");
  });

  it("shows error when password is less than 8 characters", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    renderSignUp();
    const passwordFields = screen.getAllByLabelText(/^Password/);
    const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
    await ue.type(passwordField, "pass");
    expect(passwordField).toHaveAttribute("aria-invalid", "true");

    await ue.type(passwordField, "Password123@");
    expect(passwordField).toHaveAttribute("aria-invalid", "false");
  });

  it("shows error when email is invalid format", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    renderSignUp();
    const emailField = screen.getByRole("textbox", { name: "Email Address" });

    await ue.type(emailField, "invalidemail");
    expect(emailField).toHaveAttribute("aria-invalid", "true");

    await ue.type(emailField, "test@example.com");
    expect(emailField).toHaveAttribute("aria-invalid", "false");
  });
});
