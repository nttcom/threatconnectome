import type {
  AuthContextValue,
  AuthStateCallbacks,
  EmailPasswordArgs,
  PhoneNumberExamples,
  RegisterPhoneNumberResult,
  SendEmailVerificationArgs,
  SendPasswordResetArgs,
  SignInResult,
  SignInWithEmailArgs,
  SignInWithRedirectArgs,
} from "../../hooks/auth";

export class AuthData {
  public readonly originalData: unknown;
  constructor(originalData: unknown) {
    this.originalData = originalData;
  }
}

export class AuthError extends Error {
  public readonly originalData: unknown;
  public readonly code: string | undefined;
  constructor(
    originalData: unknown,
    code: string | undefined = undefined,
    message = "Something went wrong.",
  ) {
    super(message);
    this.originalData = originalData;
    this.code = code;
  }
}

// Base class methods declare parameters for the AuthContextValue contract.
// Subclasses (FirebaseProvider, SupabaseProvider) override; the parameters
// are referenced via `void` to satisfy noUnusedParameters without using
// an `_` prefix workaround.
export class AuthProvider implements AuthContextValue {
  onAuthStateChanged(callbacks: AuthStateCallbacks): () => void {
    void callbacks;
    throw new Error("Not implemented");
  }
  async createUserWithEmailAndPassword(args: EmailPasswordArgs): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async signInWithEmailAndPassword(args: SignInWithEmailArgs): Promise<SignInResult> {
    void args;
    throw new Error("Not implemented");
  }
  async signInWithSamlPopup(): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async signInWithRedirect(args: SignInWithRedirectArgs): Promise<void> {
    void args;
    throw new Error("Not implemented");
  }
  async signOut(): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async sendEmailVerification(args: SendEmailVerificationArgs): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async sendPasswordResetEmail(args: SendPasswordResetArgs): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async verifyPasswordResetCode(args: { actionCode: string }): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async confirmPasswordReset(args: { actionCode: string; newPassword: string }): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async applyActionCode(args: { actionCode: string }): Promise<AuthData> {
    void args;
    throw new Error("Not implemented");
  }
  async registerPhoneNumber(
    phoneNumber: string,
    recaptchaId: string,
    phoneNumberExamples?: PhoneNumberExamples,
  ): Promise<RegisterPhoneNumberResult> {
    void phoneNumber;
    void recaptchaId;
    void phoneNumberExamples;
    throw new Error("Not implemented");
  }
  async deletePhoneNumber(): Promise<void> {
    throw new Error("Not implemented");
  }
  async verifySmsForLogin(
    resolver: unknown,
    verificationId: string,
    verificationCode: string,
  ): Promise<unknown> {
    void resolver;
    void verificationId;
    void verificationCode;
    throw new Error("Not implemented");
  }
  async verifySmsForEnrollment(verificationId: string, verificationCode: string): Promise<void> {
    void verificationId;
    void verificationCode;
    throw new Error("Not implemented");
  }
  async sendSmsCodeAgain(
    phoneInfoOptions: unknown,
    auth: unknown,
    recaptchaId: string,
  ): Promise<string> {
    void phoneInfoOptions;
    void auth;
    void recaptchaId;
    throw new Error("Not implemented");
  }
  isSmsAuthenticationEnabled(): boolean {
    throw new Error("Not implemented");
  }
  isAuthenticatedWithSaml(): boolean {
    throw new Error("Not implemented");
  }
  getPhoneNumber(): string | null {
    throw new Error("Not implemented");
  }
}
