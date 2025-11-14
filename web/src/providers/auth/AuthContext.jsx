import PropTypes from "prop-types";

import { AuthContext } from "../../hooks/auth";

import { AuthProviderFactory } from "./AuthProviderFactory";

export function AuthProvider(props) {
  const { children } = props;

  const authProvider = AuthProviderFactory.create();

  const onAuthStateChanged = authProvider.onAuthStateChanged;
  const createUserWithEmailAndPassword = authProvider.createUserWithEmailAndPassword;
  const signInWithEmailAndPassword = authProvider.signInWithEmailAndPassword;
  const signInWithSamlPopup = authProvider.signInWithSamlPopup;
  const signInWithRedirect = authProvider.signInWithRedirect;
  const signOut = authProvider.signOut;
  const sendEmailVerification = authProvider.sendEmailVerification;
  const sendPasswordResetEmail = authProvider.sendPasswordResetEmail;
  const verifyPasswordResetCode = authProvider.verifyPasswordResetCode;
  const confirmPasswordReset = authProvider.confirmPasswordReset;
  const applyActionCode = authProvider.applyActionCode;
  const registerPhoneNumber = authProvider.registerPhoneNumber;
  const verifySmsForEnrollment = authProvider.verifySmsForEnrollment;
  const deletePhoneNumber = authProvider.deletePhoneNumber;
  const verifySmsForLogin = authProvider.verifySmsForLogin;

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
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
AuthProvider.propTypes = {
  children: PropTypes.object,
};
