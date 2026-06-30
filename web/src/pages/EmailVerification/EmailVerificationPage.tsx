import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";

import ResetPasswordForm from "./ResetPasswordForm";
import VerifyEmail from "./VerifyEmail";

export function EmailVerification() {
  const { t } = useTranslation("emailVerification", { keyPrefix: "EmailVerificationPage" });
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const mode = params.get("mode");
  const oobCode = params.get("oobCode");

  switch (mode) {
    case "verifyEmail":
      return <VerifyEmail oobCode={oobCode} />;
    case "resetPassword":
      return <ResetPasswordForm oobCode={oobCode} />;
    case "recoverEmail":
      // future work?
      break;
    default:
      console.error("Invalid mode");
      return <>{t("invalidRequest")}</>;
  }
}
