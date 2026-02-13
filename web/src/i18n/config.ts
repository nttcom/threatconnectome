import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";
import { initReactI18next } from "react-i18next";

export const supportedLngs = {
  en: "English",
  ja: "日本語",
};

// eslint-disable-next-line import/no-named-as-default-member
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    returnEmptyString: false,
    supportedLngs: Object.keys(supportedLngs),
    // Specify the file name as the namespace only when used outside React components.
    ns: ["providers", "utils"],
    debug: false,

    // Disable it because React handles escaping.
    interpolation: {
      escapeValue: false,
    },
    react: {
      useSuspense: true,
    },
  });

export default i18n;
