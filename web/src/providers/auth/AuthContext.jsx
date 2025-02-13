import PropTypes from "prop-types";
import React from "react";

import { AuthContext } from "../../hooks/auth";

import { AuthProviderFactory } from "./AuthProviderFactory";

export function AuthProvider(props) {
  const { children } = props;

  const authProvider = AuthProviderFactory.create();

  const createUserWithEmailAndPassword = authProvider.createUserWithEmailAndPassword;
  const signInWithEmailAndPassword = authProvider.signInWithEmailAndPassword;
  const signInWithSamlPopup = authProvider.signInWithSamlPopup;
  const signOut = authProvider.signOut;
  const sendEmailVerification = authProvider.sendEmailVerification;
  const sendPasswordResetEmail = authProvider.sendPasswordResetEmail;
  const verifyPasswordResetCode = authProvider.verifyPasswordResetCode;
  const confirmPassword = authProvider.confirmPassword;

  return (
    <AuthContext.Provider
      value={{
        createUserWithEmailAndPassword,
        signInWithEmailAndPassword,
        signInWithSamlPopup,
        signOut,
        sendEmailVerification,
        sendPasswordResetEmail,
        verifyPasswordResetCode,
        confirmPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
AuthProvider.propTypes = {
  children: PropTypes.object,
};
