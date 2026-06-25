import i18n from "../i18n/config";

export type AuthErrorSource =
  | Error
  | string
  | {
      code?: string;
      message?: string;
    }
  | null
  | undefined;

type GetAuthErrorMessageOptions = {
  namespace?: string;
  keyPrefix?: string;
  defaultMessage?: string;
};

export function normalizeAuthErrorSource(error: unknown): AuthErrorSource {
  if (
    error instanceof Error ||
    typeof error === "string" ||
    error === null ||
    error === undefined
  ) {
    return error;
  }

  if (typeof error === "object") {
    return {
      code: "code" in error && typeof error.code === "string" ? error.code : undefined,
      message: "message" in error && typeof error.message === "string" ? error.message : undefined,
    };
  }

  return { message: String(error) };
}

export function getAuthErrorCode(error: AuthErrorSource): string | undefined {
  if (typeof error === "object" && error !== null && "code" in error) {
    return typeof error.code === "string" ? error.code : undefined;
  }
  return undefined;
}

export function authErrorToString(error: AuthErrorSource): string | undefined {
  if (typeof error === "object" && error !== null && "message" in error) {
    return typeof error.message === "string" ? error.message : undefined;
  }
  if (typeof error === "string") {
    return error;
  }
  return undefined;
}

export function getAuthErrorMessage(
  error: AuthErrorSource,
  options: GetAuthErrorMessageOptions = {},
): string {
  const {
    namespace = "providers",
    keyPrefix = "auth.FirebaseProvider",
    defaultMessage = "An error occurred.",
  } = options;

  const codeFromObject = getAuthErrorCode(error);
  const rawCode = codeFromObject || (typeof error === "string" ? error : "auth/internal-error");
  const code = rawCode.replace(/\//g, ".");

  const key = `${keyPrefix}.${code}`;

  if (i18n.exists(key, { ns: namespace })) {
    return i18n.t(key, { ns: namespace });
  }

  return defaultMessage;
}
