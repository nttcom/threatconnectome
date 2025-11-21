import {
  applyActionCode,
  browserSessionPersistence,
  confirmPasswordReset,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  verifyPasswordResetCode,
  multiFactor,
  RecaptchaVerifier,
  PhoneAuthProvider,
  PhoneMultiFactorGenerator,
  getMultiFactorResolver,
} from "firebase/auth";

import Firebase from "../../utils/Firebase";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

function _errorToMessage(error) {
  // TODO: should fill missing codes
  // https://firebase.google.com/docs/reference/js/auth?hl=ja#autherrorcodes
  return (
    {
      "auth/email-already-in-use": "Email already in use",
      "auth/invalid-action-code": "Invalid action code",
      "auth/invalid-email": "Invalid email format.",
      "auth/too-many-requests": "Too many requests.",
      "auth/user-disabled": "Disabled user.",
      "auth/user-not-found": "User not found.",
      "auth/wrong-password": "Wrong password.",
    }[error.code || error] ||
    error.message ||
    error.code ||
    `Something went wrong (${error}).`
  );
}

class FirebaseAuthError extends AuthError {
  constructor(error) {
    super(error, error.code, _errorToMessage(error.code));
  }
}

async function startSmsLoginFlow(auth, error) {
  const resolver = getMultiFactorResolver(auth, error);
  for (const hint of resolver.hints) {
    if (hint.factorId === PhoneMultiFactorGenerator.FACTOR_ID) {
      const phoneInfoOptions = {
        multiFactorHint: hint,
        session: resolver.session,
      };

      //Todo: RecaptchaVerifier will be implemented later.
      const recaptchaVerifier = new RecaptchaVerifier(auth, "recaptcha-container-visible-login", {
        size: "normal",
        callback: (response) => {
          // reCAPTCHA solved, you can proceed with
          // phoneAuthProvider.verifyPhoneNumber(...).
          console.log("success");
        },
      });

      try {
        const phoneAuthProvider = new PhoneAuthProvider(auth);
        const verificationId = await phoneAuthProvider.verifyPhoneNumber(
          phoneInfoOptions,
          recaptchaVerifier,
        );
        return [resolver, verificationId, phoneInfoOptions, auth];
      } catch (error) {
        recaptchaVerifier.clear();
        throw error;
      }
    }
  }
}

export class FirebaseProvider extends AuthProvider {
  onAuthStateChanged({ signInCallback, signOutCallback }) {
    const unsubscribe = onAuthStateChanged(Firebase.getAuth(), (user) => {
      if (user) {
        signInCallback();
      } else {
        signOutCallback();
      }
    });
    return unsubscribe;
  }

  async createUserWithEmailAndPassword({ email, password }) {
    return await createUserWithEmailAndPassword(Firebase.getAuth(), email, password)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async signInWithEmailAndPassword({ email, password }) {
    const auth = Firebase.getAuth();
    return await setPersistence(auth, browserSessionPersistence)
      .then(() => signInWithEmailAndPassword(auth, email, password))
      .then((result) => {
        return new AuthData(result);
      })
      .catch(async (error) => {
        if (error.code == "auth/multi-factor-auth-required") {
          return await startSmsLoginFlow(auth, error);
        } else {
          throw new FirebaseAuthError(error);
        }
      });
  }

  async signInWithSamlPopup() {
    const samlProvider = Firebase.getSamlProvider();
    if (!samlProvider) {
      throw new Error("SAML not supported");
    }
    return await signInWithPopup(Firebase.getAuth(), samlProvider)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async signOut() {
    return await signOut(Firebase.getAuth())
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async sendEmailVerification({ actionCodeSettings }) {
    return await sendEmailVerification(Firebase.getAuth().currentUser, actionCodeSettings)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async sendPasswordResetEmail({ email, actionCodeSettings }) {
    return await sendPasswordResetEmail(Firebase.getAuth(), email, actionCodeSettings)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async verifyPasswordResetCode({ actionCode }) {
    return await verifyPasswordResetCode(Firebase.getAuth(), actionCode)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async confirmPasswordReset({ actionCode, newPassword }) {
    return await confirmPasswordReset(Firebase.getAuth(), actionCode, newPassword)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async applyActionCode({ actionCode }) {
    return await applyActionCode(Firebase.getAuth(), actionCode)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  async registerPhoneNumber(phoneNumber) {
    const e164Pattern = /^\+[1-9]\d{1,14}$/;
    if (!e164Pattern.test(phoneNumber)) {
      throw new Error(
        "Invalid phone number format: Must be in E.164 format (e.g., +818012345678).",
      );
    }

    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;

    //Todo: RecaptchaVerifier will be implemented later.
    const recaptchaVerifier = new RecaptchaVerifier(
      auth,
      "recaptcha-container-visible-register-phone-number",
      {
        size: "normal",
        callback: (response) => {
          // reCAPTCHA solved, you can proceed with
          // phoneAuthProvider.verifyPhoneNumber(...).
          console.log("success");
        },
      },
    );

    try {
      const multiFactorSession = await multiFactor(currentUser).getSession();
      const phoneInfoOptions = {
        phoneNumber: phoneNumber,
        session: multiFactorSession,
      };
      const phoneAuthProvider = new PhoneAuthProvider(auth);
      return phoneAuthProvider.verifyPhoneNumber(phoneInfoOptions, recaptchaVerifier); // Send SMS verification code.
    } catch (error) {
      recaptchaVerifier.clear();
      throw error;
    }
  }

  async deletePhoneNumber() {
    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    const multiFactorUser = multiFactor(currentUser);
    for (const facter of multiFactorUser.enrolledFactors) {
      multiFactorUser.unenroll(facter);
    }
  }

  async verifySmsForLogin(resolver, verificationId, verificationCode) {
    const cred = PhoneAuthProvider.credential(verificationId, verificationCode);
    const multiFactorAssertion = PhoneMultiFactorGenerator.assertion(cred);

    // Complete sign-in.
    return resolver.resolveSignIn(multiFactorAssertion);
  }

  verifySmsForEnrollment(verificationId, verificationCode) {
    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    const cred = PhoneAuthProvider.credential(verificationId, verificationCode);
    const multiFactorAssertion = PhoneMultiFactorGenerator.assertion(cred);

    // Complete enrollment.
    multiFactor(currentUser).enroll(multiFactorAssertion, "My personal phone number");
  }

  async sendSmsCodeAgain(phoneInfoOptions, auth) {
    //Todo: RecaptchaVerifier will be implemented later.
    const recaptchaVerifier = new RecaptchaVerifier(auth, "recaptcha-container-invisible-resend", {
      size: "invisible",
      callback: (response) => {
        // reCAPTCHA solved, you can proceed with
        // phoneAuthProvider.verifyPhoneNumber(...).
        console.log("success");
      },
    });

    try {
      const phoneAuthProvider = new PhoneAuthProvider(auth);
      const verificationId = await phoneAuthProvider.verifyPhoneNumber(
        phoneInfoOptions,
        recaptchaVerifier,
      );
      return verificationId;
    } catch (error) {
      console.log(error);
    }
  }
}
