import { createContext, useContext } from "react";
import { useSelector } from "react-redux";

export function useSkipUntilAuthUserIsReady() {
  return !useSelector((state) => state.auth.authUserIsReady);
}

export const AuthContext = createContext(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("Implementation error: cannot use AuthContext");
  }
  return context;
}
