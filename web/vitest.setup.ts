import "@testing-library/jest-dom/vitest";
import i18n from "./src/i18n/config.ts";
import enStatus from "./public/locales/en/status.json";
import enResetPassword from "./public/locales/en/resetPassword.json";
import enEmailVerification from "./public/locales/en/emailVerification.json";
import enSignUp from "./public/locales/en/signUp.json";
import { vi } from "vitest";

// Ensure tests run with English and loaded translations for the status namespace
i18n.addResourceBundle("en", "status", enStatus, true, true);
// Preload EmailVerification namespace with the correct translations
i18n.addResourceBundle("en", "emailVerification", enEmailVerification, true, true);
// Preload SignUp namespace to ensure accessible names are translated in tests
i18n.addResourceBundle("en", "signUp", enSignUp, true, true);
i18n.addResourceBundle("en", "resetPassword", enResetPassword, true, true);
i18n.changeLanguage("en");
// Disable suspense to avoid async loading issues during tests
// @ts-expect-error react options exist at runtime
i18n.options.react.useSuspense = false;

// Extend default test timeout to reduce flakiness in async UI flows
vi.setConfig({ testTimeout: 10000 });
