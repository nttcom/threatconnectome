import i18n from "../i18n/config";

type AuthErrorLike = { code?: string | unknown } | string | null | undefined;

type GetAuthErrorMessageOptions = {
  namespace?: string;
  keyPrefix?: string;
  defaultMessage?: string;
};

export function getAuthErrorMessage(
  error: AuthErrorLike,
  options: GetAuthErrorMessageOptions = {},
): string {
  const {
    namespace = "providers",
    keyPrefix = "auth.FirebaseProvider",
    defaultMessage = "An error occurred.",
  } = options;

  const rawCode =
    (typeof error === "object" && error !== null && "code" in error ? error.code : undefined) ||
    (typeof error === "string" ? error : "auth/internal-error");

  const code = typeof rawCode === "string" ? rawCode.replace(/\//g, ".") : "auth.internal-error";

  const key = `${keyPrefix}.${code}`;

  if (i18n.exists(key, { ns: namespace })) {
    return i18n.t(key, { ns: namespace });
  }

  return defaultMessage;
}
