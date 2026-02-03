import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import { Provider } from "react-redux";
import { useNavigate, useLocation } from "react-router-dom";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import store from "../../../store";
import { SignUp } from "../SignUpPage";

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
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
      <AuthProvider>
        <SignUp />
      </AuthProvider>
    </Provider>,
  );
};

describe("TestSignUpPage", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      const mockCreateUserWithEmailAndPassword = vi.fn().mockResolvedValue();
      const mockSendEmailVerification = vi.fn().mockResolvedValue();
      useAuth.mockReturnValue({
        createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
        sendEmailVerification: mockSendEmailVerification,
      });
    });

    afterEach(() => {
      vi.resetAllMocks();
    });

    it("renders the heading", () => {
      renderSignUp();
      expect(screen.getByRole("heading", { name: "Threatconnectome" })).toBeInTheDocument();
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
      expect(screen.getByRole("button", { name: "Sign up" })).toBeInTheDocument();
    });

    it("renders the back to login link", () => {
      renderSignUp();
      expect(screen.getByRole("button", { name: "Back to log in" })).toBeInTheDocument();
    });
  });

  describe("Sign up button behavior", () => {
    it("creates an account when given valid parameters", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const emailValue = "test@example.com";
      const passwordValue = "Password1234@";
      const uidValue = "12345";

      const mockCreateUserWithEmailAndPassword = vi.fn().mockResolvedValue({
        user: { email: emailValue, uid: uidValue },
      });
      const mockSendEmailVerification = vi.fn().mockResolvedValue(undefined);
      useAuth.mockReturnValue({
        createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
        sendEmailVerification: mockSendEmailVerification,
      });

      renderSignUp();
      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      await ue.type(emailField, emailValue);

      const passwordFields = screen.getAllByLabelText(/^Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, passwordValue);

      await ue.click(screen.getByRole("button", { name: "Sign up" }));

      expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith({
        email: emailValue,
        password: passwordValue,
      });

      // sendEmailVerification is skipped if using Supabase or Firebase-Emulator
      /*
      expect(mockSendEmailVerification).toHaveBeenCalledWith({
        user: { email: emailValue, uid: uidValue },
        actionCodeSettings: null,
      });
      expect(
        screen.getByText("An email for verification was sent to your address."),
      ).toBeInTheDocument();
      */
      expect(mockSendEmailVerification).toBeCalledTimes(0);
      expect(screen.getByText("Signed up successfully.")).toBeInTheDocument();

      expect(screen.getByRole("button", { name: "Sign up" })).toBeDisabled();
    });
    it("handles error", async () => {
      const validEmail = "test@example.com";
      const validPassword = "Password1234@";
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const errorCode = "test error";
      const errorMessage = "Something went wrong.";

      const mockCreateUserWithEmailAndPassword = vi.fn().mockRejectedValue({
        code: errorCode,
        message: errorMessage,
      });
      const mockSendEmailVerification = vi.fn().mockResolvedValue(undefined);
      useAuth.mockReturnValue({
        createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
        sendEmailVerification: mockSendEmailVerification,
      });
      const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

      renderSignUp();
      const emailField = screen.getByRole("textbox", { name: "Email Address" });
      await ue.type(emailField, validEmail);

      const passwordFields = screen.getAllByLabelText(/^Password/);
      const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
      await ue.type(passwordField, validPassword);

      await ue.click(screen.getByRole("button", { name: "Sign up" }));

      expect(mockConsoleError).toHaveBeenCalledWith({
        code: errorCode,
        message: errorMessage,
      });

      expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith({
        email: validEmail,
        password: validPassword,
      });

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it("navigate login page when click link button", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    const mockNavigate = vi.fn();
    useNavigate.mockReturnValue(mockNavigate);

    const mockLocation = {
      state: { from: "/test_from", search: "/test_from" },
    };
    useLocation.mockReturnValue(mockLocation);

    renderSignUp();
    await ue.click(screen.getByRole("button", { name: "Back to log in" }));

    expect(mockNavigate).toHaveBeenCalledWith("/login", {
      state: {
        from: mockLocation.state.from,
        search: mockLocation.state.search,
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
    const tooShortPassword = "pass";
    const validPassword = "Password1234@";

    renderSignUp();
    const passwordFields = screen.getAllByLabelText(/^Password/);
    const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
    await ue.type(passwordField, tooShortPassword);
    expect(passwordField).toHaveAttribute("aria-invalid", "true");

    await ue.type(passwordField, validPassword);
    expect(passwordField).toHaveAttribute("aria-invalid", "false");
  });

  it("shows error when email is invalid format", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const invalidEmail = "invalid email format";

    renderSignUp();
    const emailField = screen.getByRole("textbox", { name: "Email Address" });

    await ue.type(emailField, invalidEmail);
    expect(emailField).toHaveAttribute("aria-invalid", "true");

    await ue.type(emailField, "test@example.com");
    expect(emailField).toHaveAttribute("aria-invalid", "false");
  });
});
