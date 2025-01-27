import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator, SAMLAuthProvider } from "firebase/auth";

class Firebase {
  constructor() {
    this.auth = null;
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
    if (this.samlProvider == null) {
      const providerId = import.meta.env.VITE_FIREBASE_AUTH_SAML_PROVIDER_ID;
      if (providerId) {
        this.samlProvider = new SAMLAuthProvider(providerId);
      }
    }

    return this.samlProvider;
  }
}

export default new Firebase();
