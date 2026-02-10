import { createContext, useContext } from "react";
import { useTranslation } from "react-i18next";
import { useSelector } from "react-redux";

export function useSkipUntilAuthUserIsReady() {
  return !useSelector((state) => state.auth.authUserIsReady);
}

export const AuthContext = createContext(null);

export function useAuth() {
  const context = useContext(AuthContext);
  const { t } = useTranslation("hooks", { keyPrefix: "Auth" });

  if (!context) {
    throw new Error(t("authContextUnavailable"));
  }
  return context;
}
