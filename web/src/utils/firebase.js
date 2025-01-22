import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator, SAMLAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: import.meta.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: import.meta.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

const setSamlProvider = (providerId) => {
  if (providerId) {
    return new SAMLAuthProvider(providerId);
  } else {
    return null;
  }
};
export const samlProvider = setSamlProvider(import.meta.env.REACT_APP_FIREBASE_AUTH_SAML_PROVIDER_ID);

if (import.meta.env.REACT_APP_FIREBASE_AUTH_EMULATOR_URL) {
  connectAuthEmulator(auth, import.meta.env.REACT_APP_FIREBASE_AUTH_EMULATOR_URL);
}
