import i18n from "../i18n/config";

export function getAuthErrorMessage(error, options = {}) {
  const {
    namespace = "providers",
    keyPrefix = "auth.FirebaseProvider",
    defaultMessage = "An error occurred.",
    replaceSlash = false,
  } = options;

  let code = error?.code || error || "auth/internal-error";

  if (replaceSlash && typeof code === "string") {
    code = code.replace(/\//g, ".");
  }

  const key = `${keyPrefix}.${code}`;

  if (i18n.exists(key, { ns: namespace })) {
    return i18n.t(key, { ns: namespace });
  }

  return error?.message || defaultMessage;
}
