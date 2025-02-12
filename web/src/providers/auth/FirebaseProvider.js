import {
  applyActionCode,
  browserSessionPersistence,
  confirmPasswordReset,
  createUserWithEmailAndPassword,
  sendEmailVerification,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  verifyPasswordResetCode,
} from "firebase/auth";

import Firebase from "../../utils/Firebase";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

function _codeToMessage(code) {
  return (
    {
      "auth/invalid-email": "Invalid email format.",
      "auth/too-many-requests": "Too many requests.",
      "auth/user-disabled": "Disabled user.",
      "auth/user-not-found": "User not found.",
      "auth/wrong-password": "Wrong password.",
    }[code] || "Something went wrong."
  );
}

export class FirebaseProvider extends AuthProvider {
  async signInWithEmailAndPassword({ email, password }) {
    const auth = Firebase.getAuth();
    await setPersistence(auth, browserSessionPersistence);
    return await signInWithEmailAndPassword(auth, email, password)
      .then((credential) => {
        return new AuthData(credential);
      })
      .catch((error) => {
        throw new AuthError(error, error.code, _codeToMessage(error.code));
      });
  }
}
