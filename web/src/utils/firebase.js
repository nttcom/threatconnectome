import { initializeApp } from "firebase/app";
import { getAuth, getIdToken, onAuthStateChanged, connectAuthEmulator } from "firebase/auth";

import { setToken } from "./api";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

if (process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_URL) {
  connectAuthEmulator(auth, process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_URL);
}

onAuthStateChanged(auth, async (user) => {
  if (!user) return;
  setToken(await getIdToken(user, true));
});
