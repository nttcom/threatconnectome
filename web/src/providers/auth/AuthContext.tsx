import type { ReactNode } from "react";

import { AuthContext } from "../../hooks/auth";

import { AuthProviderFactory } from "./AuthProviderFactory";

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const authProvider = AuthProviderFactory.create();

  const onAuthStateChanged = authProvider.onAuthStateChanged.bind(authProvider);
  const createUserWithEmailAndPassword =
    authProvider.createUserWithEmailAndPassword.bind(authProvider);
  const signInWithEmailAndPassword = authProvider.signInWithEmailAndPassword.bind(authProvider);
  const signInWithSamlPopup = authProvider.signInWithSamlPopup.bind(authProvider);
  const signInWithRedirect = authProvider.signInWithRedirect.bind(authProvider);
  const signOut = authProvider.signOut.bind(authProvider);
  const sendEmailVerification = authProvider.sendEmailVerification.bind(authProvider);
  const sendPasswordResetEmail = authProvider.sendPasswordResetEmail.bind(authProvider);
  const verifyPasswordResetCode = authProvider.verifyPasswordResetCode.bind(authProvider);
  const confirmPasswordReset = authProvider.confirmPasswordReset.bind(authProvider);
  const applyActionCode = authProvider.applyActionCode.bind(authProvider);
  const registerPhoneNumber = authProvider.registerPhoneNumber.bind(authProvider);
  const verifySmsForEnrollment = authProvider.verifySmsForEnrollment.bind(authProvider);
  const deletePhoneNumber = authProvider.deletePhoneNumber.bind(authProvider);
  const verifySmsForLogin = authProvider.verifySmsForLogin.bind(authProvider);
  const sendSmsCodeAgain = authProvider.sendSmsCodeAgain.bind(authProvider);
  const isSmsAuthenticationEnabled = authProvider.isSmsAuthenticationEnabled.bind(authProvider);
  const isAuthenticatedWithSaml = authProvider.isAuthenticatedWithSaml.bind(authProvider);
  const getPhoneNumber = authProvider.getPhoneNumber.bind(authProvider);

  return (
    <AuthContext.Provider
      value={{
        onAuthStateChanged,
        createUserWithEmailAndPassword,
        signInWithEmailAndPassword,
        signInWithSamlPopup,
        signInWithRedirect,
        signOut,
        sendEmailVerification,
        sendPasswordResetEmail,
        verifyPasswordResetCode,
        confirmPasswordReset,
        applyActionCode,
        registerPhoneNumber,
        deletePhoneNumber,
        verifySmsForLogin,
        verifySmsForEnrollment,
        sendSmsCodeAgain,
        isSmsAuthenticationEnabled,
        isAuthenticatedWithSaml,
        getPhoneNumber,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
