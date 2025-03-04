import { initializeApp } from "firebase/app";
import { connectAuthEmulator, getAuth, SAMLAuthProvider } from "firebase/auth";

class Firebase {
  constructor() {
    this.auth = null;
    this.providerId = null;
    this.samlProvider = null;
  }

  getAuth() {
    if (this.auth == null) {
      const firebaseConfig = {
        apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
        authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
        projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
        storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
        messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
        appId: import.meta.env.VITE_FIREBASE_APP_ID,
        measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
      };

      const app = initializeApp(firebaseConfig);

      this.auth = getAuth(app);

      if (import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL) {
        connectAuthEmulator(this.auth, import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL);
      }
    }

    return this.auth;
  }

  getSamlProvider() {
    if (this.providerId != import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID) {
      this.samlProvider = null;
    }

    if (this.samlProvider == null) {
      this.providerId = import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID;
      if (this.providerId) {
        this.samlProvider = new SAMLAuthProvider(this.providerId);
      }
    }

    return this.samlProvider;
  }

  async getBearerToken() {
    return await this.getAuth()?.currentUser?.getIdToken();
  }
}

export default new Firebase();
