import { useSelector } from "react-redux";

export function useSkipUntilAuthUserIsReady() {
  return !useSelector((state) => state.auth.authUserIsReady);
}
