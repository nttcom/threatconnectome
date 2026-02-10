import Supabase from "../../utils/Supabase";
import i18n from "../../i18n/config";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

const supabase =
  import.meta.env.VITE_AUTH_SERVICE === "supabase" ? Supabase.getClient() : undefined;

const _immediateEmitEvent = async (signInCallback, signOutCallback) => {
  const result = await supabase.auth.getSession();
  if (result.data?.session) {
    signInCallback();
  } else {
    signOutCallback();
  }
};

class SupabaseAuthError extends AuthError {
  constructor(error) {
    super(error, error.code, error.message);
  }
}

export class SupabaseProvider extends AuthProvider {
  onAuthStateChanged({ signInCallback, signOutCallback }) {
    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      switch (event) {
        case "SIGNED_IN":
          signInCallback();
          break;
        case "SIGNED_OUT":
          signOutCallback();
          break;
        default:
        // Nothing to do
      }
    });
    /* Note: Firebase emits event when called onAuthStateChanged, but Supabase does not. */
    _immediateEmitEvent(signInCallback, signOutCallback);
    return data.subscription.unsubscribe;
  }

  async createUserWithEmailAndPassword({ email, password }) {
    return await supabase.auth
      .signUp({ email, password })
      .then((result) => {
        if (!result.error) {
          return new AuthData(result);
        }
        throw new SupabaseAuthError(result.error);
      })
      .catch((error) => {
        throw error;
      });
  }

  async signInWithEmailAndPassword({ email, password }) {
    return await supabase.auth
      .signInWithPassword({ email, password })
      .then((result) => {
        if (!result.error) {
          return new AuthData(result);
        }
        throw new SupabaseAuthError(result.error);
      })
      .catch((error) => {
        throw error;
      });
  }

  async signInWithRedirect({ provider, redirectTo }) {
    let options = { redirectTo };
    switch (provider) {
      case "keycloak":
        options["scopes"] = "openid";
        break;
      default:
        throw new SupabaseAuthError({
          code: "unsupportedProvider",
          message: i18n.t("auth.SupabaseProvider.unsupportedProvider", {
            ns: "providers",
            provider: provider,
          }),
        });
    }
    await supabase.auth
      .signInWithOAuth({ provider, options })
      .then((result) => {
        if (result.error) {
          throw new SupabaseAuthError(result.error);
        }
      })
      .catch((error) => {
        throw error;
      });
  }

  async sendPasswordResetEmail({ email, redirectTo }) {
    /* Attention:
     *   if your mail server setting is not valid, resetPasswordForEmail will
     *     - FAIL if email is VALID.
     *     - SUCCEED if email is INVALID (not registered email).
     */
    return await supabase.auth
      .resetPasswordForEmail(email, { redirectTo })
      .then((result) => {
        if (!result.error) {
          return new AuthData(result);
        }
        throw new SupabaseAuthError(result.error);
      })
      .catch((error) => {
        throw error;
      });
  }

  async signOut() {
    const result = await supabase.auth.getSession();
    if (!result?.data?.session) {
      // already signed out. prevent recursive SIGNED_OUT event.
      return new AuthData(undefined);
    }
    return await supabase.auth
      .signOut()
      .then((result) => {
        if (!result.error) {
          return new AuthData(result);
        }
        throw new SupabaseAuthError(result.error);
      })
      .catch((error) => {
        throw error;
      });
  }
}
