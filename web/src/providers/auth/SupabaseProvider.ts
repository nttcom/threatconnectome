import type { SupabaseClient } from "@supabase/supabase-js";

import type {
  AuthStateCallbacks,
  EmailPasswordArgs,
  SendPasswordResetArgs,
  SignInResult,
  SignInWithEmailArgs,
  SignInWithRedirectArgs,
} from "../../hooks/auth";
import i18n from "../../i18n/config";
import Supabase from "../../utils/Supabase";
import { getAuthErrorMessage } from "../../utils/authErrorUtils";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

const supabase: SupabaseClient | undefined =
  import.meta.env.VITE_AUTH_SERVICE === "supabase" ? Supabase.getClient() : undefined;

const _immediateEmitEvent = async (
  signInCallback: () => void,
  signOutCallback: () => void,
): Promise<void> => {
  if (!supabase) return;
  const result = await supabase.auth.getSession();
  if (result.data?.session) {
    signInCallback();
  } else {
    signOutCallback();
  }
};

type ErrorLike = { code?: string; message?: string } | unknown;

function _errorToMessage(error: ErrorLike): string {
  const message = getAuthErrorMessage(error as never, {
    namespace: "providers",
    keyPrefix: "auth.SupabaseProvider",
    defaultMessage: i18n.t("auth.SupabaseProvider.internal-error", { ns: "providers" }),
  });
  return message;
}

class SupabaseAuthError extends AuthError {
  constructor(error: ErrorLike) {
    const code = (error as { code?: string })?.code;
    const message = (error as { message?: string })?.message;
    super(error, code, _errorToMessage(error));
    console.error("Authentication error:", message);
  }
}

const assertSupabase = (): SupabaseClient => {
  if (!supabase) {
    throw new SupabaseAuthError({
      code: "supabaseNotConfigured",
      message: "Supabase client is not configured",
    });
  }
  return supabase;
};

export class SupabaseProvider extends AuthProvider {
  override onAuthStateChanged({ signInCallback, signOutCallback }: AuthStateCallbacks): () => void {
    const client = assertSupabase();
    const { data } = client.auth.onAuthStateChange((event) => {
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
    return () => data.subscription.unsubscribe();
  }

  override async createUserWithEmailAndPassword({
    email,
    password,
  }: EmailPasswordArgs): Promise<AuthData> {
    const client = assertSupabase();
    return await client.auth
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

  override async signInWithEmailAndPassword({
    email,
    password,
  }: SignInWithEmailArgs): Promise<SignInResult> {
    const client = assertSupabase();
    return await client.auth
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

  override async signInWithRedirect({
    provider,
    redirectTo,
  }: SignInWithRedirectArgs): Promise<void> {
    const client = assertSupabase();
    const options: { redirectTo: string; scopes?: string } = { redirectTo };
    switch (provider) {
      case "keycloak":
        options.scopes = "openid";
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
    await client.auth
      // Supabase types accept a finite set of providers; cast since validation occurs above.
      // any: @supabase/supabase-js requires a Provider literal type incompatible with our open string param.
      .signInWithOAuth({ provider: provider as never, options })
      .then((result) => {
        if (result.error) {
          throw new SupabaseAuthError(result.error);
        }
      })
      .catch((error) => {
        throw error;
      });
  }

  override async sendPasswordResetEmail({
    email,
    redirectTo,
  }: SendPasswordResetArgs): Promise<AuthData> {
    /* Attention:
     *   if your mail server setting is not valid, resetPasswordForEmail will
     *     - FAIL if email is VALID.
     *     - SUCCEED if email is INVALID (not registered email).
     */
    const client = assertSupabase();
    return await client.auth
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

  override async signOut(): Promise<AuthData> {
    const client = assertSupabase();
    const result = await client.auth.getSession();
    if (!result?.data?.session) {
      // already signed out. prevent recursive SIGNED_OUT event.
      return new AuthData(undefined);
    }
    return await client.auth
      .signOut()
      .then((signOutResult) => {
        if (!signOutResult.error) {
          return new AuthData(signOutResult);
        }
        throw new SupabaseAuthError(signOutResult.error);
      })
      .catch((error) => {
        throw error;
      });
  }
}
