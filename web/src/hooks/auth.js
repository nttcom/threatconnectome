import Firebase from "../utils/Firebase";

export function useSkipUntilAuthUserIsReady() {
  const auth = Firebase.getAuth();
  const skip = auth.currentUser === null || auth.currentUser === undefined;

  return skip;
}
