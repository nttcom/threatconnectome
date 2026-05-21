import type {
  ActionCodeSettings,
  Auth,
  MultiFactorResolver,
  PhoneInfoOptions,
  UserCredential,
} from "firebase/auth";
import { createContext, useContext } from "react";
import { useTranslation } from "react-i18next";
import { useSelector } from "react-redux";

import type { RootState } from "../store";
import type { AuthData } from "../providers/auth/AuthProvider";

export function useSkipUntilAuthUserIsReady(): boolean {
  return !useSelector((state: RootState) => state.auth.authUserIsReady);
}

export type AuthStateCallbacks = {
  signInCallback: () => void;
  signOutCallback: () => void;
};

export type EmailPasswordArgs = {
  email: string;
  password: string;
};

export type SignInWithEmailArgs = EmailPasswordArgs & {
  recaptchaId?: string;
};

export type SendEmailVerificationArgs = {
  actionCodeSettings: ActionCodeSettings | null;
};

export type SendPasswordResetArgs = {
  email: string;
  actionCodeSettings?: ActionCodeSettings;
  redirectTo?: string;
};

export type SignInWithRedirectArgs = {
  provider: "keycloak";
  redirectTo: string;
};

export type PhoneNumberExamples = {
  nationalExample?: string;
  internationalExample?: string;
};

export type SmsLoginFlow = {
  mfa: true;
  resolver: MultiFactorResolver;
  verificationId: string;
  phoneInfoOptions: PhoneInfoOptions;
  auth: Auth;
};

export type SignInResult = AuthData | SmsLoginFlow | undefined;

export type RegisterPhoneNumberResult = {
  verificationId: string;
  phoneInfoOptions: PhoneInfoOptions;
  auth: Auth;
};

export interface AuthContextValue {
  onAuthStateChanged: (callbacks: AuthStateCallbacks) => () => void;
  createUserWithEmailAndPassword: (args: EmailPasswordArgs) => Promise<AuthData>;
  signInWithEmailAndPassword: (args: SignInWithEmailArgs) => Promise<SignInResult>;
  signInWithSamlPopup: () => Promise<AuthData>;
  signInWithRedirect: (args: SignInWithRedirectArgs) => Promise<void>;
  signOut: () => Promise<AuthData>;
  sendEmailVerification: (args: SendEmailVerificationArgs) => Promise<AuthData>;
  sendPasswordResetEmail: (args: SendPasswordResetArgs) => Promise<AuthData>;
  verifyPasswordResetCode: (args: { actionCode: string }) => Promise<AuthData>;
  confirmPasswordReset: (args: { actionCode: string; newPassword: string }) => Promise<AuthData>;
  applyActionCode: (args: { actionCode: string }) => Promise<AuthData>;
  registerPhoneNumber: (
    phoneNumber: string,
    recaptchaId: string,
    phoneNumberExamples?: PhoneNumberExamples,
  ) => Promise<RegisterPhoneNumberResult>;
  deletePhoneNumber: () => Promise<void>;
  verifySmsForLogin: (
    resolver: MultiFactorResolver,
    verificationId: string,
    verificationCode: string,
  ) => Promise<UserCredential>;
  verifySmsForEnrollment: (verificationId: string, verificationCode: string) => Promise<void>;
  sendSmsCodeAgain: (
    phoneInfoOptions: PhoneInfoOptions,
    auth: Auth,
    recaptchaId: string,
  ) => Promise<string>;
  isSmsAuthenticationEnabled: () => boolean;
  isAuthenticatedWithSaml: () => boolean;
  getPhoneNumber: () => string | null;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  const { t } = useTranslation("hooks", { keyPrefix: "Auth" });

  if (!context) {
    throw new Error("AUTH_CONTEXT_UNAVAILABLE: " + t("authContextUnavailable"));
  }
  return context;
}
