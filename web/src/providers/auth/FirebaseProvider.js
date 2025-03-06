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
      .catch((error) => {
        throw new FirebaseAuthError(error);
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
}
