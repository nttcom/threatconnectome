import { auth } from "../utils/firebase";

export function useSkipUntilAuthUserIsReady() {
  const skip = auth.currentUser === null || auth.currentUser === undefined;

  return skip;
}
