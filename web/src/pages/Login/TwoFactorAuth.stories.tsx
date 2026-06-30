import type { UserCredential } from "firebase/auth";

import { AuthContext, type AuthContextValue } from "../../hooks/auth";
import { AuthData } from "../../providers/auth/AuthProvider";

import { TwoFactorAuth } from "./TwoFactorAuth";

const mockAuthData = {
  verificationId: "mock-verification-id-12345",
  resolver: {},
  phoneInfoOptions: {},
  auth: {},
} as Parameters<typeof TwoFactorAuth>[0]["authData"];

const mockNavigateInternalPage = async () => {};

const createMockAuthContext = (overrides: Partial<AuthContextValue> = {}): AuthContextValue => ({
  onAuthStateChanged: () => () => undefined,
  createUserWithEmailAndPassword: async () => new AuthData(undefined),
  signInWithEmailAndPassword: async () => new AuthData(undefined),
  signInWithSamlPopup: async () => new AuthData(undefined),
  signInWithRedirect: async () => undefined,
  signOut: async () => new AuthData(undefined),
  sendEmailVerification: async () => new AuthData(undefined),
  sendPasswordResetEmail: async () => new AuthData(undefined),
  verifyPasswordResetCode: async () => new AuthData(undefined),
  confirmPasswordReset: async () => new AuthData(undefined),
  applyActionCode: async () => new AuthData(undefined),
  registerPhoneNumber: async () => {
    throw new Error("Not implemented");
  },
  deletePhoneNumber: async () => undefined,
  verifySmsForLogin: async () => ({}) as UserCredential,
  verifySmsForEnrollment: async () => undefined,
  sendSmsCodeAgain: async () => "new-verification-id-67890",
  isSmsAuthenticationEnabled: () => false,
  isAuthenticatedWithSaml: () => false,
  getPhoneNumber: () => null,
  ...overrides,
});

export default {
  component: TwoFactorAuth,
};

export const SuccessfulVerification = () => {
  const mockAuthContext = createMockAuthContext({
    verifySmsForLogin: async () => ({}) as UserCredential,
    sendSmsCodeAgain: () => Promise.resolve("new-verification-id-67890"),
  });

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <TwoFactorAuth authData={mockAuthData} navigateInternalPage={mockNavigateInternalPage} />
    </AuthContext.Provider>
  );
};

export const InvalidCode = () => {
  const mockAuthContext = createMockAuthContext({
    verifySmsForLogin: () => {
      const error = new Error("Invalid verification code") as Error & { code: string };
      error.code = "auth/invalid-verification-code";
      return Promise.reject(error);
    },
    sendSmsCodeAgain: () => Promise.resolve("new-verification-id-67890"),
  });

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <TwoFactorAuth authData={mockAuthData} navigateInternalPage={mockNavigateInternalPage} />
    </AuthContext.Provider>
  );
};
