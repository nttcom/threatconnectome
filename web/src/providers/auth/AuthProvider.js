export class AuthData {
  constructor(originalData) {
    this.originalData = originalData;
  }
}

export class AuthError extends Error {
  constructor(originalData, code = undefined, message = "Something went wrong.") {
    super(message);
    this.originalData = originalData;
    this.code = code;
  }
}

export class AuthProvider {
  onAuthStateChanged() {
    // should return unsubscribe handler
    throw new Error("Not implemented");
  }
  async createUserWithEmailAndPassword() {
    throw new Error("Not implemented");
  }
  async signInWithEmailAndPassword() {
    throw new Error("Not implemented");
  }
  async signInWithSamlPopup() {
    throw new Error("Not implemented");
  }
  async signInWithRedirect() {
    // for OAuth
    throw new Error("Not implemented");
  }
  async signOut() {
    throw new Error("Not implemented");
  }
  async sendEmailVerification() {
    throw new Error("Not implemented");
  }
  async sendPasswordResetEmail() {
    throw new Error("Not implemented");
  }
  async verifyPasswordResetCode() {
    throw new Error("Not implemented");
  }
  async confirmPasswordReset() {
    throw new Error("Not implemented");
  }
}
