import { AuthContext } from "../../hooks/auth";

import { TwoFactorAuth } from "./TwoFactorAuth";

const mockAuthData = {
  verificationId: "mock-verification-id-12345",
  resolver: {},
  phoneInfoOptions: {},
  auth: {},
};

const mockNavigateInternalPage = () => {};

export default {
  title: "Login/TwoFactorAuth",
  component: TwoFactorAuth,
};

export const SuccessfulVerification = () => {
  const mockAuthContext = {
    verifySmsForLogin: () => Promise.resolve(),
    sendSmsCodeAgain: () => Promise.resolve("new-verification-id-67890"),
  };

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <TwoFactorAuth authData={mockAuthData} navigateInternalPage={mockNavigateInternalPage} />
    </AuthContext.Provider>
  );
};

export const InvalidCode = () => {
  const mockAuthContext = {
    verifySmsForLogin: () => {
      const error = new Error("Invalid verification code");
      error.code = "auth/invalid-verification-code";
      return Promise.reject(error);
    },
    sendSmsCodeAgain: () => Promise.resolve("new-verification-id-67890"),
  };

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <TwoFactorAuth authData={mockAuthData} navigateInternalPage={mockNavigateInternalPage} />
    </AuthContext.Provider>
  );
};

export const GenericError = () => {
  const mockAuthContext = {
    verifySmsForLogin: () => {
      const error = new Error("Network error occurred");
      return Promise.reject(error);
    },
    sendSmsCodeAgain: () => Promise.resolve("new-verification-id-67890"),
  };

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <TwoFactorAuth authData={mockAuthData} navigateInternalPage={mockNavigateInternalPage} />
    </AuthContext.Provider>
  );
};
