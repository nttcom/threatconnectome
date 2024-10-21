import { useSelector } from "react-redux";

export function useSkipUntilAuthTokenIsReady() {
  const authToken = useSelector((state) => state.auth.token);
  const skip = authToken === undefined;
  return skip;
}
