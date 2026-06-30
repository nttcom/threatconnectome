import type { Meta } from "@storybook/react-vite";

import { AuthContext, type AuthContextValue } from "../../hooks/auth";
import { AuthData } from "../../providers/auth/AuthProvider";
import ResetPasswordForm from "./ResetPasswordForm";

const meta = {
  component: ResetPasswordForm,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ResetPasswordForm>;

export default meta;

export const Default = () => {
  const mockAuthContext: AuthContextValue = {
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
    verifySmsForLogin: async () => {
      throw new Error("Not implemented");
    },
    verifySmsForEnrollment: async () => undefined,
    sendSmsCodeAgain: async () => "new-verification-id-67890",
    isSmsAuthenticationEnabled: () => false,
    isAuthenticatedWithSaml: () => false,
    getPhoneNumber: () => null,
  };
  const oobCode = "demo-oob-code";

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <ResetPasswordForm oobCode={oobCode} />
    </AuthContext.Provider>
  );
};
