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

const setupDefaultAuthMock = () => {
  useAuth.mockReturnValue({
    createUserWithEmailAndPassword: vi.fn().mockResolvedValue(),
    sendEmailVerification: vi.fn().mockResolvedValue(),
    signOut: vi.fn().mockResolvedValue(undefined),
  });
};

describe("TestSignUpPage", () => {
  describe("Rendering", () => {
    beforeEach(() => {
      setupDefaultAuthMock();
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
    afterEach(() => {
      vi.restoreAllMocks();
    });

    // it("creates an account when given valid parameters", async () => {
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    //   const emailValue = "test@example.com";
    //   const passwordValue = "Password1234@";
    //   const confirmPassword = "Password1234@";
    //   const uidValue = "12345";

    //   const mockCreateUserWithEmailAndPassword = vi.fn().mockResolvedValue({
    //     user: { email: emailValue, uid: uidValue },
    //   });
    //   const mockSendEmailVerification = vi.fn().mockResolvedValue(undefined);
    //   useAuth.mockReturnValue({
    //     createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
    //     sendEmailVerification: mockSendEmailVerification,
    //     signOut: vi.fn().mockResolvedValue(undefined),
    //   });

    //   renderSignUp();
    //   const emailField = screen.getByRole("textbox", { name: "Email Address" });
    //   await ue.type(emailField, emailValue);

    //   const passwordInputs = screen.getAllByLabelText(/^Password/i);
    //   const passwordField = passwordInputs.find((el) => el.tagName === "INPUT");

    //   const confirmInputs = screen.getAllByLabelText(/^Confirm Password/i);
    //   const confirmField = confirmInputs.find((el) => el.tagName === "INPUT");

    //   await ue.type(passwordField, passwordValue);
    //   await ue.type(confirmField, confirmPassword);

    //   await ue.click(screen.getByRole("button", { name: "Sign up" }));

    //   expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith({
    //     email: emailValue,
    //     password: passwordValue,
    //   });

    //   // sendEmailVerification is skipped if using Supabase or Firebase-Emulator
    //   /*
    //   expect(mockSendEmailVerification).toHaveBeenCalledWith({
    //     user: { email: emailValue, uid: uidValue },
    //     actionCodeSettings: null,
    //   });
    //   expect(
    //     screen.getByText("An email for verification was sent to your address."),
    //   ).toBeInTheDocument();
    //   */
    //   expect(mockSendEmailVerification).toBeCalledTimes(0);
    //   expect(screen.getByText("Signed up successfully.")).toBeInTheDocument();

    //   expect(screen.getByRole("button", { name: "Sign up" })).toBeDisabled();
    // });
    // it("handles error", async () => {
    //   const validEmail = "test@example.com";
    //   const validPassword = "Password1234@";
    //   const confirmPassword = "Password1234@";
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    //   const errorCode = "auth/email-already-in-use";
    //   const errorMessage = "Something went wrong.";

    //   const mockCreateUserWithEmailAndPassword = vi.fn().mockRejectedValue({
    //     code: errorCode,
    //     message: errorMessage,
    //   });
    //   const mockSendEmailVerification = vi.fn().mockResolvedValue(undefined);
    //   useAuth.mockReturnValue({
    //     createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
    //     sendEmailVerification: mockSendEmailVerification,
    //     signOut: vi.fn().mockResolvedValue(undefined),
    //   });
    //   const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

    //   renderSignUp();
    //   const emailField = screen.getByRole("textbox", { name: "Email Address" });
    //   await ue.type(emailField, validEmail);

    //   const passwordInputs = screen.getAllByLabelText(/^Password/i);
    //   const passwordField = passwordInputs.find((el) => el.tagName === "INPUT");

    //   const confirmInputs = screen.getAllByLabelText(/^Confirm Password/i);
    //   const confirmField = confirmInputs.find((el) => el.tagName === "INPUT");

    //   await ue.type(passwordField, validPassword);
    //   await ue.type(confirmField, confirmPassword);

    //   await ue.click(screen.getByRole("button", { name: "Sign up" }));

    //   expect(mockConsoleError).toHaveBeenCalledWith({
    //     code: errorCode,
    //     message: errorMessage,
    //   });

    //   expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith({
    //     email: validEmail,
    //     password: validPassword,
    //   });

    //   expect(screen.getByText("Email already in use")).toBeInTheDocument();
    // });

    it("shows error.message when translation key does not exist", async () => {
      const validEmail = "test@example.com";
      const validPassword = "Password1234@";
      const confirmPassword = "Password1234@";
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const errorCode = "auth/unknown-error";
      const errorMessage = "This is a provider-translated error message.";
      const defaultMessage = "An internal error occurred. Please try again later."; //See web/src/pages/SignUp/SignUpPage.jsx::getAuthErrorMessage      const fallbackMessage = getAuthErrorMessage(error, {

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

      const passwordInputs = screen.getAllByLabelText(/^Password/i);
      const passwordField = passwordInputs.find((el) => el.tagName === "INPUT");

      const confirmInputs = screen.getAllByLabelText(/^Confirm Password/i);
      const confirmField = confirmInputs.find((el) => el.tagName === "INPUT");

      await ue.type(passwordField, validPassword);
      await ue.type(confirmField, confirmPassword);

      await ue.click(screen.getByRole("button", { name: "Sign up" }));

      expect(mockConsoleError).toHaveBeenCalledWith({
        code: errorCode,
        message: errorMessage,
      });
      screen.debug();
      expect(screen.getByText(defaultMessage)).toBeInTheDocument();
    });

    //   it("shows internal error message when error.code is missing", async () => {
    //     const validEmail = "test@example.com";
    //     const validPassword = "Password1234@";
    //     const confirmPassword = "Password1234@";
    //     const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    //     const mockCreateUserWithEmailAndPassword = vi.fn().mockRejectedValue({
    //       message: undefined,
    //     });
    //     const mockSendEmailVerification = vi.fn().mockResolvedValue(undefined);
    //     useAuth.mockReturnValue({
    //       createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
    //       sendEmailVerification: mockSendEmailVerification,
    //     });
    //     const mockConsoleError = vi.spyOn(console, "error").mockImplementation(() => {});

    //     renderSignUp();
    //     const emailField = screen.getByRole("textbox", { name: "Email Address" });
    //     await ue.type(emailField, validEmail);

    //     const passwordInputs = screen.getAllByLabelText(/^Password/i);
    //     const passwordField = passwordInputs.find((el) => el.tagName === "INPUT");

    //     const confirmInputs = screen.getAllByLabelText(/^Confirm Password/i);
    //     const confirmField = confirmInputs.find((el) => el.tagName === "INPUT");

    //     await ue.type(passwordField, validPassword);
    //     await ue.type(confirmField, confirmPassword);

    //     await ue.click(screen.getByRole("button", { name: "Sign up" }));

    //     expect(mockConsoleError).toHaveBeenCalled();
    //     expect(
    //       screen.getByText("An internal error occurred. Please try again later."),
    //     ).toBeInTheDocument();
    //   });
    // });

    // it("navigate login page when click link button", async () => {
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    //   setupDefaultAuthMock();

    //   const mockNavigate = vi.fn();
    //   useNavigate.mockReturnValue(mockNavigate);

    //   const mockLocation = {
    //     state: { from: "/test_from", search: "/test_from" },
    //   };
    //   useLocation.mockReturnValue(mockLocation);

    //   renderSignUp();
    //   await ue.click(screen.getByRole("button", { name: "Back to log in" }));

    //   expect(mockNavigate).toHaveBeenCalledWith("/login", {
    //     state: {
    //       from: mockLocation.state.from,
    //       search: mockLocation.state.search,
    //     },
    //   });
    // });

    // it("change password mask when click visibility icon button", async () => {
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });

    //   setupDefaultAuthMock();

    //   renderSignUp();
    //   const passwordFields = screen.getAllByLabelText(/^Password/);
    //   const passwordField = passwordFields.find((el) => el.tagName === "INPUT");

    //   expect(passwordField).toHaveAttribute("type", "password");

    //   await ue.click(screen.getByLabelText("toggle password visibility"));

    //   expect(passwordField).toHaveAttribute("type", "text");
    // });

    // it("shows error when password is less than 8 characters", async () => {
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    //   const tooShortPassword = "pass";
    //   const validPassword = "Password1234@";

    //   setupDefaultAuthMock();

    //   renderSignUp();
    //   const passwordFields = screen.getAllByLabelText(/^Password/);
    //   const passwordField = passwordFields.find((el) => el.tagName === "INPUT");
    //   await ue.type(passwordField, tooShortPassword);
    //   expect(passwordField).toHaveAttribute("aria-invalid", "true");

    //   await ue.type(passwordField, validPassword);
    //   expect(passwordField).toHaveAttribute("aria-invalid", "false");
    // });

    // it("shows error when email is invalid format", async () => {
    //   const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    //   const invalidEmail = "invalid email format";

    //   setupDefaultAuthMock();

    //   renderSignUp();
    //   const emailField = screen.getByRole("textbox", { name: "Email Address" });

    //   await ue.type(emailField, invalidEmail);
    //   expect(emailField).toHaveAttribute("aria-invalid", "true");

    //   await ue.type(emailField, "test@example.com");
    //   expect(emailField).toHaveAttribute("aria-invalid", "false");
  });
});
