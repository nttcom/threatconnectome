import Supabase from "../../utils/Supabase";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

const supabase = Supabase.getClient();

export class SupabaseProvider extends AuthProvider {
  async signInWithEmailAndPassword({ email, password }) {
    return await supabase.auth
      .signInWithPassword({ email, password })
      .then((result) => {
        if (!result.error) {
          return new AuthData(result);
        }
        throw new AuthError(result, result.error.code, result.error.message);
      })
      .catch((error) => {
        throw error;
      });
  }
}
