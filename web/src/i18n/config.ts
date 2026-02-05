import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";
import { initReactI18next } from "react-i18next";

export const supportedLngs = {
  en: "English",
  ja: "日本語",
};

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    returnEmptyString: false,
    supportedLngs: Object.keys(supportedLngs),
    debug: false,

    // Disable it because React handles escaping.
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
