import type { AuthResponse, SupabaseClient } from "@supabase/supabase-js";
import type { UserCredential } from "firebase/auth";

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
  SmsLoginFlow,
} from "../../hooks/auth";
import type { AuthErrorSource } from "../../utils/authErrorUtils";

export type SupabaseSignOutResponse = Awaited<ReturnType<SupabaseClient["auth"]["signOut"]>>;
export type AuthDataSource =
  | AuthResponse
  | SupabaseSignOutResponse
  | UserCredential
  | string
  | void;

export class AuthData<TOriginalData extends AuthDataSource = AuthDataSource> {
  public readonly originalData: TOriginalData;
  constructor(originalData: TOriginalData) {
    this.originalData = originalData;
  }
}

export class AuthError<TOriginalData extends AuthErrorSource = AuthErrorSource> extends Error {
  public readonly originalData: TOriginalData;
  public readonly code: string | undefined;
  constructor(
    originalData: TOriginalData,
    code: string | undefined = undefined,
    message = "Something went wrong.",
  ) {
    super(message);
    this.originalData = originalData;
    this.code = code;
  }
}

export class AuthProvider implements AuthContextValue {
  onAuthStateChanged(_callbacks: AuthStateCallbacks): () => void {
    throw new Error("Not implemented");
  }
  async createUserWithEmailAndPassword(_args: EmailPasswordArgs): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async signInWithEmailAndPassword(_args: SignInWithEmailArgs): Promise<SignInResult> {
    throw new Error("Not implemented");
  }
  async signInWithSamlPopup(): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async signInWithRedirect(_args: SignInWithRedirectArgs): Promise<void> {
    throw new Error("Not implemented");
  }
  async signOut(): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async sendEmailVerification(_args: SendEmailVerificationArgs): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async sendPasswordResetEmail(_args: SendPasswordResetArgs): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async verifyPasswordResetCode(_args: { actionCode: string }): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async confirmPasswordReset(_args: {
    actionCode: string;
    newPassword: string;
  }): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async applyActionCode(_args: { actionCode: string }): Promise<AuthData> {
    throw new Error("Not implemented");
  }
  async registerPhoneNumber(
    _phoneNumber: string,
    _recaptchaId: string,
    _phoneNumberExamples?: PhoneNumberExamples,
  ): Promise<RegisterPhoneNumberResult> {
    throw new Error("Not implemented");
  }
  async deletePhoneNumber(): Promise<void> {
    throw new Error("Not implemented");
  }
  async verifySmsForLogin(
    _resolver: SmsLoginFlow["resolver"],
    _verificationId: string,
    _verificationCode: string,
  ): ReturnType<AuthContextValue["verifySmsForLogin"]> {
    throw new Error("Not implemented");
  }
  async verifySmsForEnrollment(_verificationId: string, _verificationCode: string): Promise<void> {
    throw new Error("Not implemented");
  }
  async sendSmsCodeAgain(
    _phoneInfoOptions: RegisterPhoneNumberResult["phoneInfoOptions"],
    _auth: RegisterPhoneNumberResult["auth"],
    _recaptchaId: string,
  ): Promise<string> {
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
